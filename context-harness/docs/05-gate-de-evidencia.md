# Gate de Evidência (`EVIDENCE.md`)

## Quando este artefato se aplica

Só quando o sistema expõe alguma forma de veredito, recomendação ou score ao
usuário final — não é exclusivo de sistemas de trading. Qualquer "o sistema sugere
X", "este padrão indica Y", "confiança: alta" é uma afirmação implícita de que
alguém mediu que aquilo funciona. Na maioria dos projetos isso nunca foi medido —
foi implementado porque "faz sentido" ou porque é um padrão conhecido na área.
`EVIDENCE.md` fecha esse gap tornando a lacuna visível em vez de escondida.

## A regra

> **Nenhum elemento com formato de veredito aparece em nenhuma superfície (payload
> de API, UI, relatório, notificação) sem uma linha em `EVIDENCE.md` que o sustente.**

Cada linha registra:

- **O sinal/comportamento** e onde ele aparece (quais superfícies).
- **O cálculo** — arquivo/função responsável.
- **Status**, de um enum fechado. Sugestão de enum genérico (adaptar ao domínio):
  - `sem-medicao` — existe, nunca foi testado.
  - `sem-edge` / `nao-confirmado` — testado, não se sustenta.
  - `edge-condicional[contexto]` — funciona só em certas condições, nomeadas.
  - `com-edge` / `confirmado` — testado e se sustenta.
  - `amostra-insuficiente` — teste rodado, N pequeno demais para conclusão.
- **Artefato** — o que prova o status (arquivo de resultado, notebook, log de teste),
  não uma afirmação sem lastro.
- **Veredito em prosa** — o resultado real, incluindo direção que não confirmou,
  inconsistência entre condições testadas, e o histórico de remedições (uma linha
  pode ser corrigida mais de uma vez conforme bugs de metodologia são achados —
  isso é normal e deve ficar registrado, não escondido).

## Por que isto evita o erro mais comum

O padrão mais perigoso em sistemas de recomendação/score é medir uma vez, sem teste
de significância, ver "a direção bate" nas células observadas, e declarar vitória. O
caso de origem teve exatamente isso: um veredito de "funciona" foi registrado sem
nenhum teste estatístico — só observação de que a direção parecia certa em 4
células. Quando alguém rodou um teste de significância de verdade (Welch t-test)
depois, nenhuma célula era significativa — a consistência aparente era ruído
plausível, não sinal. `EVIDENCE.md` não evita esse erro sozinho, mas cria o hábito
de escrever "testado com [método], p=X, N=Y" em vez de "parece que funciona", o que
torna o erro visível na hora da revisão.

## Gate de mudança

Mudar o cálculo de qualquer sinal que já tem linha em `EVIDENCE.md` **exige
re-medição da linha correspondente antes de ir a produção** — os dois resultados
(antes/depois) ficam commitados junto, nunca só o depois. Sinal novo em qualquer
superfície exige a linha nova antes do merge, não depois "quando der tempo".

## Relação com a suíte de validação

`EVIDENCE.md` é o *registro* do veredito; a suíte de validação (ex.
`tests/calibration/` no caso de origem) é o que *produz* o veredito. Uma suíte
determinística, com seed fixa e reprodutibilidade byte-a-byte, é o gate real — o
`EVIDENCE.md` só existe para não deixar o resultado dessa suíte se perder ou ficar
implícito na cabeça de quem rodou.
