# Como revisar um PR Tier 1

Revisão sem spec é adivinhação. Revisão com spec é checklist.

## Princípio

Você revisa em **três passes rasos**, não um passe profundo. Cada passe responde uma pergunta única.

```
Passe 1: A spec está completa e correta?
Passe 2: Os testes cobrem a spec?
Passe 3: O código passa nos testes?
```

Se o passe 1 falha, devolve. Não adianta revisar código contra spec ruim.

## Passe 1 — Auditoria da spec (5-10 min)

Sem olhar o código. Só lê a spec.

### Checklist
- [ ] Tem todas as 5 seções (Identificação, Pré, Efeito, Invariantes, Casos limite)?
- [ ] Tem **pelo menos 3 invariantes negativas** explícitas? (Tier 1 com 0-2 invariantes é suspeito)
- [ ] Existe `[DECIDIR]` não resolvido? **Bloqueia o PR.**
- [ ] Para cada filtro/critério da operação, há invariante negativa correspondente?
- [ ] Há invariante de conservação (contagem total)?
- [ ] Casos limite cobrem entrada vazia, duplicada, fronteira?

### Pergunta-teste
> "Se eu der só esta spec para outro dev (ou outra IA) e pedir para implementar, ele tem informação suficiente para acertar tudo? Ou ainda precisa adivinhar?"

Se precisa adivinhar → spec incompleta → devolve.

## Passe 2 — Cobertura dos testes (10-15 min)

Agora abre o PR. Olha **só os testes**, não o código de produção ainda.

### Checklist
- [ ] Cada invariante negativa tem teste explícito? (busque por nome, ex: `naoDeveAfetarCampanhasForaDoPeriodo`)
- [ ] Cada caso limite da spec tem teste?
- [ ] Há teste de **conservação** (asserção sobre contagem total / soma de algo)?
- [ ] Os testes verificam estado do banco, não só retorno da função?
- [ ] Há teste de idempotência (rodar duas vezes = rodar uma)?

### Anti-padrão clássico
Teste que valida o efeito desejado mas não a ausência de efeito colateral:

```java
// FRACO — só valida o que aconteceu
assertEquals(0, campanhaRepo.findByLojaIdAndPeriodo(L, P).size());

// FORTE — valida o que aconteceu E o que NÃO aconteceu
assertEquals(0, campanhaRepo.findByLojaIdAndPeriodo(L, P).size());
assertEquals(qtdAntesOutrosPeriodos, campanhaRepo.findByLojaIdAndPeriodoNot(L, P).size());
assertEquals(qtdAntesOutrasLojas, campanhaRepo.findByLojaIdNot(L).size());
```

Se os testes só têm o estilo "fraco", a IA implementou o caminho feliz e nada protege das invariantes.

## Passe 3 — Código de produção (10-30 min)

Só agora lê o código. Com spec e testes em mente, esse passe vira raso.

### Checklist
- [ ] Cada query / filtro do código corresponde a uma invariante ou efeito da spec?
- [ ] Há código "defensivo" sem critério explícito? (`if (x != null)` sem razão clara)
- [ ] Há chamada cross-service / cross-context que não foi declarada na spec?
- [ ] Há lógica duplicada com outro service? (gatilho clássico de overlap)
- [ ] Transação cobre toda a operação? Em caso de falha parcial, comportamento bate com spec?

## Quando devolver

Devolva o PR se **qualquer** um destes for verdadeiro:

1. Spec tem `[DECIDIR]` não resolvido
2. Spec tem <3 invariantes em operação Tier 1
3. Existe invariante na spec sem teste correspondente
4. Existe teste de invariante que verifica só o caminho feliz (sem asserção negativa / de conservação)
5. Código toca entidade não declarada na spec
6. Operação destrutiva sem teste de conservação (contagem total)

Devolução não é falha — é o protocolo funcionando.

## Tempo esperado

Revisão de PR Tier 1 com spec bem escrita: **30-45 min**.

Se está levando >1h, ou a spec está ruim (volta ao passe 1) ou o PR está grande demais (peça para quebrar).

## Anti-padrão de revisão

> "Vou rodar local para entender o que faz."

Se você precisa rodar para entender, a spec falhou. Não compense leitura ruim de spec com investigação manual — devolve para o autor melhorar a spec antes.
