# licitacoes-mcp agent contract

## Mission and canonical location

Servidor MCP somente-leitura para licitações públicas brasileiras (PNCP + Compras.gov.br).
Repositório público: `https://github.com/cYoren/licitacoes-mcp`.
Cópia canônica na VPS: `/root/projects/licitacoes-mcp`.

## Hard rules

1. **Somente leitura.** Nunca adicione `POST`, `PUT`, `PATCH` ou `DELETE` contra as fontes.
   O servidor descobre, detalha e compara preço. Não submete proposta, não autentica,
   não representa ninguém em disputa.
2. **Sem credencial.** As fontes são públicas. Não introduza chave de API, token ou login.
3. **Sem inventar endpoint.** Todo caminho vem das especificações OpenAPI oficiais
   (`https://pncp.gov.br/pncp-api/v3/api-docs`, `https://dadosabertos.compras.gov.br/v3/api-docs`)
   e é validado ao vivo antes de virar ferramenta.
4. **Proveniência visível.** Toda resposta aponta para o link oficial do PNCP.
   Nunca apresente dado derivado como se fosse o documento original.

## Verification before commit

```bash
pytest -m "not live"        # offline, obrigatório
pytest                      # inclui fumaça contra as APIs reais
python -c "from licitacoes_mcp.server import server; print(server.name)"
```

Um endpoint novo só entra depois de uma chamada real bem-sucedida registrada em `tests/test_live.py`.

## Known source behaviour

- Ambas as fontes exigem `tamanhoPagina >= 10`.
- O detalhe da contratação migrou de `/api/pncp/v1/...` para `/api/consulta/v1/...`.
- A URL pública de uma contratação é `https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}`.
  O índice de busca devolve `item_url` como `/compras/...`, que responde 404. Nunca copie
  esse campo: reconstrua a URL a partir de `orgao_cnpj`, `ano` e `numero_sequencial`
  (use `sources.link_pncp`).
- O endpoint de consulta devolve a unidade em `unidadeOrgao`; `unidadeAdministrativa`
  vem nulo. Aceite os dois.
- A busca textual (`/api/search/`) devolve ~90 campos por documento; sempre normalize.
- A busca textual não é documentada no OpenAPI, mas é estável e é a que o próprio site usa.
- Rate limit real: chamadas sequenciais rápidas podem falhar. Respeite o retry/backoff do cliente.

## Publication

Repositório público. Antes de publicar: sem credencial, sem dado pessoal, sem URL interna da VPS,
`LICENSE` presente, `README` com uso verificável.
