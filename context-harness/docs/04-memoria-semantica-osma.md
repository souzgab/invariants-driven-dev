# Memória Semântica Local (camada opcional — padrão OSMA)

> Nome de origem: **OSMA** (Olympo Semantic Memory Architecture). Generalizado aqui
> como padrão de "memória semântica local em 4 tiers" — o nome específico não
> importa, a estrutura de tiers sim.

## Quando vale a pena

Esta camada **não é ponto de partida**. Ela resolve um problema específico: em
repos grandes, "onde isso está implementado?" e "quem depende deste módulo?" viram
perguntas caras de responder por grep manual, e injetar o repo inteiro no prompt
não cabe. Se o projeto ainda é pequeno o suficiente para que grep/Read resolvam em
segundos, adotar isto é custo de manutenção sem benefício.

## As 4 tiers

```
+-----------------------------------------------------------------------+
|  Tier 1 (Semantic)    — embeddings locais (ex. LanceDB +               |
|                          SentenceTransformers), busca por proximidade  |
|                          cosseno; fallback textual (ex. SQLite FTS5)   |
|  Tier 2 (Topological) — repomap simplificado, injetado direto no       |
|                          prompt do agente                              |
|  Tier 3 (Structural)  — grafo de AST local (ex. KuzuDB): imports,      |
|                          classes, assinaturas de função                |
|  Tier 4 (Active)      — cache de diffs e arquivos salvos recentemente  |
+-----------------------------------------------------------------------+
```

- **Tier 1** responde "onde no código isso é implementado, semanticamente" mesmo
  quando o termo de busca não bate literalmente com o nome da função.
- **Tier 2** dá ao agente uma visão estrutural compacta do projeto sem custo de
  tokens de ler cada arquivo.
- **Tier 3** responde "o que depende disto" e "quais são as assinaturas dos alvos"
  via query de grafo, não via leitura de arquivo por arquivo.
- **Tier 4** prioriza o que foi tocado por último — o que está "quente" na sessão
  atual.

## Como operar (3 componentes)

1. **Indexação inicial** — varre o código, extrai relações de AST (classes, funções,
   imports) para o grafo estrutural, e gera embeddings locais para a camada
   semântica.
   ```bash
   python scripts/osma_indexer.py
   ```
2. **Sincronização incremental** — daemon de monitoramento; todo arquivo salvo é
   reindexado de forma debounced (ex. 1s) via hash de controle (ex. xxHash) para
   evitar reindexar arquivo idêntico.
   ```bash
   python scripts/osma_watcher.py
   ```
3. **Exposição via MCP** — servidor Model Context Protocol local expõe as tiers como
   ferramentas que qualquer cliente MCP (Claude Code, Cursor) pode chamar:
   - `search_codebase(query)` — busca semântica com fallback textual.
   - `get_file_dependencies(file_path)` — imports diretos + assinaturas dos alvos.
   - `get_codebase_repomap()` — visualização estrutural compacta do projeto.
   ```bash
   fastmcp run scripts/osma_mcp.py
   ```

## Integração com clientes MCP

Registrar o servidor local nas configurações do cliente (`.claude/mcp.json` ou
equivalente):

```json
{
  "mcpServers": {
    "osma": {
      "command": "/caminho/para/.venv/bin/python",
      "args": ["/caminho/para/scripts/osma_mcp.py"]
    }
  }
}
```

## Cuidado com conflito de dependências

Um servidor MCP local costuma depender de uma versão de `mcp`/`fastmcp`/`starlette`
que pode conflitar com a versão que o próprio backend do projeto usa (ex. FastAPI
travado numa `starlette` mais antiga). Isso já causou bloqueio real no caso de
origem — a app não subia porque as duas dependências exigiam faixas de `starlette`
mutuamente exclusivas. Antes de compartilhar o mesmo `.venv` entre app e servidor
MCP, avalie se vale a pena um ambiente virtual separado só para a camada OSMA.
