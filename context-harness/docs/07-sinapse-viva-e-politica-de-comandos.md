# Sinapse Viva & Política de Execução de Comandos

## O que é a Sinapse Viva

Em um repositório assistido por agentes de IA autônomos, não basta o agente saber o estado do projeto (`STATUS.md`) e as convenções de código (`AGENTS.md`). É necessário que o agente saiba **o que ele pode executar** e **quais comandos exigem autorização humana prévia**.

A **Sinapse Viva** é a camada de alinhamento entre a capacidade de execução do repositório (scripts CLI, tarefas Make, testes) e o agente de IA, garantindo que o agente navegue pelo ecossistema sem realizar operações destrutivas ou gastar recursos indevidamente.

---

## As Duas Peças do Modelo

### 1. Política de Execução (`COMMAND_POLICY`)

Toda ação ou comando no repositório é classificado em uma de três políticas estritas:

| Política | Significado | Exemplo de Comandos |
|---|---|---|
| `auto` | Comandos read-only ou de verificação segura. O agente pode disparar autonomamente. | `pytest`, `git status`, `ritual status`, `npm test` |
| `confirm` | Comandos que consomem recursos (LLM, APIs) ou alteram estados locais. O agente deve pedir confirmação do usuário antes de disparar. | `ritual sintetizar`, `npm run build`, `pytest --integration` |
| `never` | Comandos de alta sensibilidade ou tomada de decisão humana. O agente é **estritamente proibido** de disparar via chat/ferramentas. | `ritual decidir`, `git push --force`, `drop database`, `deploy prod` |

### 2. Catálogo de Comandos (`COMMAND-CATALOG.md`)

O catálogo é a representação pública legível por máquina dos comandos disponíveis no repositório.

- **Regra de Ouro**: O `COMMAND-CATALOG.md` deve ser **gerado automaticamente por código** (ex: inspecionando rotas CLI Typer/Click/Argparse ou `Makefile`), nunca editado à mão.
- Se o repositório mudar a assinatura de um comando, re-gera-se o catálogo via script (ex: `python cli.py catalog`).

---

## Como Implementar no Repositório

### Passo 1: Definir o Registro da Política no Código

Em um arquivo central do repositório (ex: `pipeline/catalog.py` ou `scripts/catalog.py`), declare a tabela de política:

```python
COMMAND_POLICY = {
    "status": "auto",
    "test": "auto",
    "sintetizar": "confirm",
    "decidir": "never",
    "fechar": "never",
}
```

### Passo 2: Expor ao Agente em `AGENTS.md`

Adicione a seção de Sinapse Viva no `AGENTS.md`:

```markdown
## Política de Comandos (COMMAND_POLICY)

- Comandos `auto` rodam direto (ex: `pytest -q`, `git status`).
- Comandos `confirm` exigem confirmação do operador (ex: `sintetizar`).
- Comandos `never` NUNCA são disparados autonomamente pelo agente (ex: `decidir`, `fechar`).
```

---

## Benefícios do Padrão

1. **Prevenção de Scope Drift em Runtime**: O agente nunca toma decisões de produto sozinho ou faz deploys sem autorização.
2. **Custo Controlado**: Chamadas de LLM ou APIs pagas não são executadas em loops acidentais.
3. **Consistência de Interface**: Tanto o CLI do projeto quanto a interface de Chat do agente operam sob a mesma fonte de verdade.
