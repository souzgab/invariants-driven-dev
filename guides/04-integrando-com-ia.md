# Integrando com IAs (Devin, Copilot, Cursor, Bedrock)

A spec só funciona se a IA **realmente consumir** ela. Anexar arquivo no contexto não basta — o modelo otimiza para "produzir output que parece aderente," e ignora restrições se elas não estiverem operacionalmente ativas no fluxo.

## Princípios

1. **A spec é input obrigatório, não opcional.** Sem spec, o agente não gera código de Tier 1.
2. **A IA gera testes ANTES do código.** Cada invariante vira teste primeiro. Implementação vem depois, pressionada pelos testes.
3. **Um auditor LLM separado revisa o diff.** Não é o mesmo modelo que escreveu — papel adversarial explícito.
4. **Operação Tier 1 não passa por agente autônomo sem checkpoint humano.** Devin pode executar end-to-end em Tier 2-3, mas em Tier 1 sempre tem gate humano antes do merge.

## Prompt pattern para geração

### Template do pedido

```
Esta é uma operação TIER 1 (alto risco). Siga o protocolo:

1. Leia a spec em [caminho/spec.md]
2. Se houver [DECIDIR] não resolvido, PARE e me peça resolução. NÃO invente.
3. Gere os testes PRIMEIRO, um por invariante e um por caso limite.
   - Para cada invariante negativa, o teste deve ter asserção EXPLÍCITA
     verificando que o estado fora do escopo permanece inalterado.
   - Inclua teste de conservação (contagem total antes/depois).
4. Só depois implemente o código de produção.
5. Rode os testes. Se qualquer um falhar, NÃO ajuste o teste. Ajuste o código.
6. No final, me retorne:
   - Lista de invariantes da spec → nome do teste correspondente
   - Casos limite → nome do teste
   - Qualquer comportamento implementado que NÃO está na spec (potencial gap de spec)

NÃO use código defensivo sem critério explícito. Se você está prestes a escrever
`if (x != null)` ou similar sem que a spec mencione, PARE e me pergunte por quê.
```

### Por que cada cláusula importa

| Cláusula | O que protege |
|---|---|
| "PARE em [DECIDIR]" | Impede a invenção que causou o incidente original |
| "Testes PRIMEIRO" | TDD forçado — IA não pode pular invariante "esquecendo" |
| "Asserção EXPLÍCITA do estado fora do escopo" | Bloqueia teste fraco que só valida caminho feliz |
| "Não ajuste o teste" | Modelos têm tendência a ajustar o teste para passar |
| "Comportamento não na spec" | Captura gap de spec retroativamente |
| "Sem código defensivo sem critério" | Bloqueia o `if (id != null)` que apagou tudo |

## Auditor LLM (segundo passe)

Use um modelo diferente, ou pelo menos uma sessão limpa, com este prompt:

```
Você é um auditor adversarial. Assuma que este PR tem bug. Sua tarefa é prová-lo.

Inputs:
- Spec: [conteúdo de spec.md]
- Diff do PR: [diff completo]
- Arquivos tocados (full): [arquivos]

Para cada invariante listada na spec:
1. Existe teste que verifica? Cite o nome exato.
2. O teste tem asserção sobre o estado FORA do escopo da operação?
3. Se a invariante não tiver teste, escreva o teste que falta.

Depois, responda adversarialmente:
4. Existe alguma invariante IMPLÍCITA do domínio que a spec não capturou?
   Pense em: cascata para entidades relacionadas, efeito em filas/eventos,
   comportamento sob concorrência, idempotência.
5. Existe código no diff que sugere comportamento NÃO declarado na spec?
   Procure por queries, filtros, chamadas de service não justificadas.
6. Em que cenário esta operação destruiria dado que não deveria?
   Cite o cenário concreto, com exemplo de input.

Sua nota não é "código está bom." Sua nota é a lista de gaps encontrados.
Se você não encontrou gap, releia a spec e tente de novo.
```

## Configuração por ferramenta

### Cursor
- Coloca a spec em `.cursor/rules/` ou referencia explicitamente em cada chat
- Use `@spec.md` para forçar inclusão no contexto
- Em `.cursorrules`: regra global "operações em entidades [Campanha, Apuração, ...] requerem spec.md ao lado do arquivo"

### Devin
- Spec vai no playbook da task
- Prompt template vira parte da instrução inicial
- Habilita gate de aprovação humana antes de PR final em Tier 1
- Auditor LLM como step explícito no plano

### Copilot
- Menos controle sobre contexto. Use principalmente para Tier 2-3.
- Para Tier 1, use Cursor ou Devin com spec carregada.

### Bedrock (uso direto via API)
- Spec vai no system prompt ou como primeiro user message
- Auditor LLM = segunda chamada com modelo diferente (ex: gerar com Claude Sonnet, auditar com Claude Opus, ou vice-versa)

## Anti-padrão: "a IA leu a spec"

A IA confirmar que leu a spec não significa que vai respeitar. Validação real é:

- O código gerado tem **um teste por invariante listada**? (verifica)
- O auditor LLM, lendo independentemente, chega às mesmas conclusões? (verifica)
- O diff não tem chamadas / queries não justificadas? (verifica)

"Sim, li e entendi" do agente é ruído. Ignore.

## Métrica de sucesso do protocolo

Depois de 3-5 PRs Tier 1 sob o protocolo, mede:

- **Tempo total** (escrita de spec + geração + revisão) vs. tempo do fluxo antigo
- **Gaps encontrados em revisão** que teriam passado no fluxo antigo
- **Gaps encontrados em produção** (objetivo: zero)
- **Quantas vezes a spec teve [DECIDIR]** (sinal de tácito ficando explícito — bom)

Se o tempo total for >2x do fluxo antigo e gaps em produção forem comparáveis, o protocolo está caro demais. Simplifica formato.

Se o tempo for ~1.3x e gaps em produção zerarem, está funcionando.
