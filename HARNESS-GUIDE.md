# Guia de Adoção: Context Harness Protocol

Este guia detalha as instruções e o passo a passo para adotar o **Context Harness** em qualquer projeto de software. O objetivo é manter humanos e agentes de Inteligência Artificial (de qualquer plataforma ou IDE) alinhados ao estado real e histórico de decisões do repositório, mitigando os riscos de *scope drift* (desvio de escopo) e *token bloat* (estouro de contexto) entre sessões de trabalho.

---

## 🧭 1. O Racional: "Artefatos sobre Memória"

Modelos de linguagem não possuem memória persistente entre sessões de desenvolvimento (cada inicialização do agente ou "cold-start" começa com a janela de contexto limpa). Tentar injetar todo o histórico do projeto, logs de chat anteriores ou longas documentações narrativas causa **perda de atenção** (*lost-in-the-middle*) e desperdício de tokens.

O protocolo Context Harness resolve isso ao separar o **Estado Executável** (código, testes) do **Estado Cognitivo** (contexto, decisões, tarefas). Ele propõe a criação de 4 artefatos de texto simples na raiz ou na pasta de documentação do repositório:

1.  **`docs/STATUS.md` (Estado Vivo):** Descreve onde o projeto está, quais tarefas/requisitos estão em andamento e qual a branch ativa de desenvolvimento.
2.  **`AGENTS.md` (Convenções de Código):** Diretrizes de engenharia extraídas do código que *já existe* no repositório (convenções de estilo, tratamento de erro, regras de validação e restrições críticas).
3.  **`docs/DECISIONS.md` (Log de Decisões):** Registro *append-only* (apenas adição) de decisões técnicas e de arquitetura com IDs sequenciais únicos (ex: `D-001`, `D-002`).
4.  **`docs/EVIDENCE.md` (Métricas & Evidências):** Registro estatístico e empírico que sustenta decisões de negócio ou regras de validação complexas expostas ao usuário final.

---

## 📖 2. Como Ler o Harness (Instruções para o Agente de IA)

Para garantir o melhor uso da janela de contexto e evitar que o agente alucine ou reescreva código consolidado, a leitura dos arquivos de contexto **deve** seguir estritamente esta ordem a cada nova sessão de trabalho:

```
1. .agents/STATUS_VIVO.json (Opcional - Snapshot dinâmico do Git lido por máquina)
2. docs/STATUS.md          (Lê o topo para saber "Você está aqui" e a branch ativa)
3. AGENTS.md                (Lê por completo — contém as regras estáveis do código)
4. docs/DECISIONS.md       (NÃO lê por completo. Faz buscas por termos específicos da tarefa)
5. docs/EVIDENCE.md        (NÃO lê por completo. Só consulta se a tarefa alterar cálculos críticos)
```

---

## 🔄 3. Ciclo de Sustentação Dinâmica

Documentações narrativas e resumos manuais de encerramento de sessão tendem a ficar obsoletos rapidamente conforme novos commits ocorrem. O Context Harness resolve isso usando sustentação automatizada via script.

Ao finalizar qualquer sessão de trabalho com alterações materiais, execute o script de sincronização:
```bash
python scripts/update_harness.py
```

### O que o script faz:
1. Detecta a branch atual e os hashes/mensagens dos últimos commits usando comandos do Git.
2. Identifica os arquivos modificados recentemente.
3. Extrai as especificações de design ativas (ex: `SDD-01`) de dentro do `STATUS.md`.
4. Extrai os IDs das últimas decisões documentadas no `DECISIONS.md`.
5. Estima e exibe a volumetria de tokens ativa dos arquivos do harness para monitorar o orçamento de contexto (teto recomendado de **~25k tokens**).
6. Consolida as informações no arquivo compacto `.agents/STATUS_VIVO.json`.

*Nota: O arquivo `STATUS_VIVO.json` é projetado para leitura rápida por máquina no cold-start, servindo como o primeiro ponto de verdade factual antes da narrativa humana.*

---

## 🏗️ 4. Como Replicar em um Novo Projeto (Passo a Passo)

### Passo 1: Criar a Estrutura de Pastas
Na raiz do seu repositório, crie a estrutura de documentação básica:
- Crie o diretório `docs/` e a subpasta `docs/archive/` (onde serão arquivados registros antigos de status e decisões quando ultrapassarem o teto de tokens).
- Crie o diretório `scripts/` (ou `.agents/scripts/`) para scripts de utilidade.

### Passo 2: Copiar os Arquivos de Template
Copie os arquivos de modelo disponíveis na pasta `context-harness/templates/` deste repositório para o seu projeto:
- `AGENTS.md` (na raiz do seu repositório)
- `docs/STATUS.md`
- `docs/DECISIONS.md`
- `docs/EVIDENCE.md` (opcional - use se seu projeto possui lógica analítica ou estatística)
- `scripts/update_harness.py`

### Passo 3: Configurar os Parâmetros do Script
Edite o arquivo `scripts/update_harness.py` copiado para ajustar os caminhos e os padrões de nomenclatura de tarefas do seu projeto:
```python
STATUS_PATH = "docs/STATUS.md"
DECISIONS_PATH = "docs/DECISIONS.md"
# Expressão regular para encontrar a tarefa ativa em STATUS.md (ex: SDD-01 ou TASK-123)
ACTIVE_SPEC_PATTERN = r"(SDD-\d+-[a-zA-Z0-9\-_.]+)" 
```

### Passo 4: Estabelecer os Gates de Maturidade
Documente explicitamente no rodapé de seu `AGENTS.md` os limites operacionais para o agente de IA:
- **Nível 1 (Ativo):** Ações livres (criar arquivos sob specs, rodar testes, atualizar status).
- **Nível 2+ (Gated - Bloqueado):** Exige confirmação humana expressa antes de executar (ex: alterar configurações de CI/CD, adicionar dependências de pacotes, refatorar código legado fora do escopo da tarefa atual).

---

## ⚡ 5. Integração com Invariants-Driven Development (IDD)

O **Context Harness** garante o alinhamento contextual ao longo de múltiplas sessões. Para tarefas de **alto risco** (Tier 1 - ex: operações destrutivas no banco de dados, cálculos financeiros ou de pontuação, alterações em logs de auditoria), o harness deve ser complementado com o protocolo de Invariantes:

1.  Crie uma especificação para a tarefa a partir do template `templates/invariants.md`.
2.  Descreva detalhadamente o efeito positivo esperado e as **Invariantes Negativas** (o que a operação **NÃO PODE** alterar ou tocar).
3.  Instrua o agente de IA a criar os cenários de teste para cada invariante negativa **antes** de implementar a lógica de produção (TDD).
4.  Submeta a especificação e o código a um agente auditor adversarial (utilizando o prompt em `templates/prompt-auditor.md`) em uma sessão separada para buscar brechas na lógica.

---

## 📂 6. Histórico e Estudos de Caso (Origem)

Este protocolo foi desenvolvido a partir de aprendizados empíricos em cenários de desenvolvimento assistido por IA de alta complexidade:
*   Para um estudo de caso real detalhado contendo a aplicação prática e números de performance do protocolo de harness, consulte o documento: `context-harness/examples/olympo-case-study.md`.
*   Para a discussão conceitual e histórica que originou a especificação de invariantes negativas em operações destrutivas e financeiras, consulte: `docs/conversations/2026-05-04-genese-do-protocolo.md`.
