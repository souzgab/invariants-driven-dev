# Quando usar este protocolo

Aplicar invariants-driven em **toda história** é teatro burocrático. O protocolo só funciona se o escopo for restrito a operações onde o custo de erro >> custo de escrever a spec.

## Critérios de classificação

Uma operação é **Tier 1** (requer spec com invariantes) se atende **qualquer um** dos critérios abaixo:

### 1. Destrutiva
- Deleta registros de banco
- Sobrescreve estado sem versionamento
- Move dado para arquivo morto / soft delete em massa
- Reset de qualquer contador, saldo ou estado

### 2. Financeira ou de incentivo
- Calcula, debita, ou credita pontos / cashback / comissão
- Aplica regra de premiação
- Apura resultado de campanha
- Encerra ou cancela benefício

### 3. Afeta histórico
- Altera registros de períodos passados
- Recalcula valor já comunicado ao usuário
- Reprocessa eventos antigos
- Modifica dado de auditoria

### 4. Difícil de reverter
- Dispara comunicação externa (e-mail, push, SMS, webhook)
- Aciona integração com sistema parceiro que não aceita compensação
- Persiste em sistema de terceiros

### 5. Operação em lote / batch
- Processa CSV / arquivo de entrada
- Itera sobre N entidades aplicando regra
- Consume fila e aplica efeito acumulado

## Critérios que **não** justificam Tier 1

| Critério inválido | Por quê |
|---|---|
| "É código complexo" | Complexidade pede testes, não spec formal |
| "É código novo" | Novidade não é risco por si só |
| "Toca várias entidades" | Acoplamento estrutural, não risco semântico |
| "Vai pra produção" | Tudo vai. Critério vazio. |

## Como decidir em 30 segundos

```
Pergunta 1: Se essa operação rodar errado em produção, dá para reverter
            sem cliente perceber e sem reprocessamento manual?

  - SIM → Tier 2 ou 3. Fluxo normal.
  - NÃO → Pergunta 2.

Pergunta 2: O comportamento errado pode (a) destruir dado, (b) afetar
            saldo/pontos/dinheiro de cliente, ou (c) disparar comunicação
            indevida?

  - SIM → Tier 1. Aplica protocolo.
  - NÃO → Tier 2.
```

## Exemplo de Domínio (ex: Campanhas, Pontuação, Gamificação)

Lista de exemplo de operações Tier 1 a serem mapeadas junto com o Tech Lead:

- [ ] Exclusão de campanha (qualquer escopo)
- [ ] Encerramento ou expiração forçada de benefícios
- [ ] Ingestão de arquivos em lote (CSV/JSON -> persistência)
- [ ] Apuração de pontos / processamento de saldos
- [ ] Recálculo retroativo de histórico financeiro ou de pontuação
- [ ] Atribuição ou revogação manual de acessos críticos
- [ ] Reset/fechamento de períodos de apuração contábil
- [ ] Processamento de filas de mensageria com efeito persistente e não-idempotente
- [ ] Migração destrutiva de dados entre versões de schema

## Anti-padrão de escopo

Se mais de **20% das histórias** do sprint estão sendo classificadas como Tier 1, o critério está sendo aplicado largo demais. Vai virar fricção e o time vai abandonar o protocolo. Recalibre.
