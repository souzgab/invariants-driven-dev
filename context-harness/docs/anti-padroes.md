# Anti-padrões observados (e por que evitá-los)

Registrados a partir de incidentes reais no caso de origem — não são hipotéticos.

## "Resumo de compactação" escrito à mão

Um arquivo tipo `compact_summary.md`, escrito por um agente ao final de uma sessão
longa para "economizar contexto na próxima", parece uma boa ideia e falha na
prática: fica desatualizado assim que o próximo commit acontece. No caso de origem,
um resumo escrito numa sessão dizia que duas tarefas específicas "não tinham
começado"; ambas foram implementadas e commitadas **ainda no mesmo dia**, e o
arquivo permaneceu incorreto até alguém notar por acaso.

**Correção:** não escrever resumo à mão. Gerar o snapshot por script determinístico
a partir do `git log` e dos próprios arquivos do harness (ver
[`02-ciclo-de-sustentacao-dinamica.md`](02-ciclo-de-sustentacao-dinamica.md)). Se um
arquivo desse tipo já existir no repo, marque-o explicitamente como obsoleto no
próprio arquivo, apontando para a fonte de verdade real — não delete silenciosamente
algo que outra sessão possa ainda estar referenciando, mas deixe claríssimo que não
é para ser lido como estado.

## Veredito sem teste de significância

Declarar que um sinal/padrão/heurística "funciona" porque a direção observada bate
com a expectativa em algumas células de teste, sem nenhum teste estatístico formal.
No caso de origem, isso gerou um veredito de "com edge" que sobreviveu por várias
sessões até alguém rodar um teste de significância de verdade — nenhuma célula era
estatisticamente significativa; a consistência aparente era ruído plausível.

**Correção:** ver [`05-gate-de-evidencia.md`](05-gate-de-evidencia.md) — todo
veredito exige método de teste nomeado, N, e p-valor (ou equivalente) registrado,
não só "a direção bateu".

## `AGENTS.md` aspiracional

Escrever em `AGENTS.md` o padrão que se *gostaria* que o código seguisse, em vez do
que ele realmente segue hoje. Um agente que confia nesse arquivo aspiracional para
entender convenções vai escrever código consistente com uma realidade que não
existe, ampliando a divergência em vez de reduzi-la.

**Correção:** toda entrada em `AGENTS.md` deve ser verificável abrindo o código
existente. Divergência desejada vira decisão registrada em `DECISIONS.md` ou próximo
passo em `STATUS.md`, não uma reescrita silenciosa da realidade no arquivo de
convenções.

## Ler `DECISIONS.md`/`EVIDENCE.md` inteiros em todo cold-start

Derrota o propósito do harness (evitar token bloat) e reintroduz o problema de
"lost in the middle" que o harness existe para prevenir.

**Correção:** grep dirigido pelo tópico da tarefa atual. Ler na íntegra só quando a
tarefa é especificamente "auditar todo o histórico de decisões" ou equivalente.

## Nível 2 decidido unilateralmente pelo agente

Um agente que, "porque parecia óbvio", configura CI, introduz `pytest` num projeto
que só tinha scripts ad-hoc, ou refatora código morto fora do escopo pedido — sem
que o dono do projeto tenha aprovado essa mudança de nível.

**Correção:** ver [`03-niveis-de-maturidade-e-gate.md`](03-niveis-de-maturidade-e-gate.md).
A lista de itens travados deve estar escrita literalmente no `AGENTS.md`, e qualquer
ambiguidade sobre se algo é Nível 1 ou 2 deve ser resolvida perguntando, não
assumindo.
