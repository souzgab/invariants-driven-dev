# Linter de Conformidade como Guarda de Regressão do Harness

## O problema

`AGENTS.md` acumula regras não-negociáveis ao longo do tempo — coisas que, se
quebradas, corrompem o sistema silenciosamente (ex.: "todo indicador precisa de
guard de `NaN` antes de comparar com threshold", "cálculo em `t` só pode usar dados
até `t`, nunca lookahead", "nunca engolir exceção retornando um valor neutro"). Um
`AGENTS.md` bem escrito documenta essas regras, mas documentação não impede
violação: código novo escrito sob pressão, ou por um agente que não releu o arquivo
inteiro, reintroduz o mesmo bug já corrigido uma vez.

## A solução: linter estático baseado em AST

Um script que percorre a árvore sintática do código (não regex sobre texto) e
levanta uma classe de verificação por regra registrada em `AGENTS.md`:

```bash
# Varredura completa
python scripts/quant_linter.py

# Arquivo ou diretório específico
python scripts/quant_linter.py --path app/internal/analysis.py

# Testes do próprio linter (regras precisam de teste também)
python -m app.tests.test_quant_linter
```

Regras de exemplo (adaptar ao domínio do projeto):

1. Toda leitura de coluna vetorizada é convertida para o dtype esperado antes do
   cálculo (evita falha silenciosa de bibliotecas de cálculo numérico com dtype
   errado).
2. Todo acesso ao último valor de uma série potencialmente em warm-up é precedido
   por checagem de NaN.
3. Nenhuma comparação usa um índice temporal futuro em relação ao índice corrente
   (guarda contra lookahead bias).
4. Nenhum `print()` de debug em código de produção — logger apenas.
5. Nenhum bloco `except` vazio ou que engole a exceção sem logar contexto.

## Como o linter deve evoluir

- **Alinhamento obrigatório com `AGENTS.md`:** toda vez que uma regra
  não-negociável nova (ou restrição nova) entra em `AGENTS.md`, uma classe de
  verificação correspondente entra no linter **no mesmo commit** — as duas coisas
  nascem juntas, nunca uma sem a outra.
- **Exit code como contrato:** violações de regra crítica retornam código de saída
  diferente de zero, para servir de gate de pre-commit local se o projeto já estiver
  em Nível 2 (ver `03-niveis-de-maturidade-e-gate.md` — introduzir o hook em si é
  Nível 2, o script em si pode existir e rodar manualmente em Nível 1).
- **Warning vs. erro crítico é uma escolha explícita por regra:** regras que
  indicam risco real de corrupção de dado são erro crítico por padrão; regras mais
  cosméticas (ex. exceção engolida silenciosamente sem lógica de negócio crítica
  dependendo dela) podem ser warning por padrão, com uma flag `--strict` para
  promovê-las a erro quando o projeto decidir apertar o padrão.

## O que o linter não substitui

Não é framework de teste (não roda comportamento, só estrutura estática) e não
substitui a suíte de validação empírica de `05-gate-de-evidencia.md`. Ele pega a
classe de bug "óbvio de ver, fácil de esquecer sob pressão" antes que chegue a
produção; não mede se um sinal tem edge ou se um cálculo está certo.
