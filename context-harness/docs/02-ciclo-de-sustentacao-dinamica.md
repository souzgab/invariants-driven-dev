# Ciclo de Sustentação Dinâmica

## O problema que isso resolve

Um resumo de estado escrito à mão por um agente no fim de uma sessão ("compactação")
parece uma boa ideia e falha na prática: fica desatualizado assim que o próximo
commit acontece, e ninguém tem incentivo de manter um arquivo cujo único consumidor
é o próximo cold-start. O caso de origem teve exatamente esse incidente — um
`compact_summary.md` escrito numa sessão dizia que duas tarefas "não tinham
começado"; ambas foram implementadas e commitadas **ainda no mesmo dia**. O arquivo
ficou lá, errado, até alguém notar.

A correção não foi "escrever resumos melhores". Foi **parar de escrever resumo à
mão** e gerar o snapshot por script, direto do `git log` e dos próprios arquivos do
harness — uma fonte que não pode ficar desatualizada porque é recalculada, não
lembrada.

## O que o script faz

`scripts/update_harness.py` (template em [`../templates/update_harness.py`](../templates/update_harness.py)):

1. Detecta a raiz do git e a branch atual.
2. Lê o hash/mensagem/data do último commit (`git log -1`).
3. Lista os arquivos tocados nos últimos commits (`git log -5 --name-only`).
4. Extrai a spec/tarefa ativa fazendo regex sobre `STATUS.md` (ex. padrão
   `SDD-\d+-[nome]`, adaptável ao formato de spec do projeto).
5. Extrai as últimas decisões fazendo regex sobre os cabeçalhos de `DECISIONS.md`
   (ex. `^## D-\d+`).
6. Calcula uma estimativa de tokens do harness ativo (tamanho em bytes / 4, por
   arquivo) e soma um total.
7. Escreve tudo em `.agents/STATUS_VIVO.json` — um JSON compacto, não um markdown.

## Quando rodar

Ao final de qualquer sessão de trabalho com mudança material — não é preciso rodar
a cada commit trivial, mas nenhuma sessão deveria terminar sem essa atualização se
tocou código, decisão ou spec.

```bash
python scripts/update_harness.py
✅ .agents/STATUS_VIVO.json atualizado
   Branch: <branch>
   Último commit: <hash> — <mensagem>
   Tokens do harness: ~XXk
```

## Por que JSON, e por que "consumido antes de STATUS.md"

`STATUS_VIVO.json` existe para ser lido por máquina primeiro — parsing determinístico,
sem ambiguidade de markdown, e pequeno o suficiente para caber em qualquer prompt de
sistema. Ele não substitui `STATUS.md` (que tem a narrativa e o "porquê"); ele é o
snapshot que diz ao agente "isto aqui é o que está literalmente verdadeiro agora,
antes de você ler qualquer narrativa que possa estar um dia desatualizada".

## Higiene do diretório de estado

Bancos de dados locais de camadas opcionais (ex. o índice vetorial de
`04-memoria-semantica-osma.md`), logs temporários de cooperação entre agentes, e
buffers de sincronização não são artefatos do projeto — são scaffolding de sessão.
Devem estar no `.gitignore`, nunca commitados junto com `STATUS_VIVO.json`.
