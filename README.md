# licitacoes-mcp

[![cYoren/licitacoes-mcp MCP server](https://glama.ai/mcp/servers/cYoren/licitacoes-mcp/badges/score.svg)](https://glama.ai/mcp/servers/cYoren/licitacoes-mcp)

Servidor [MCP](https://modelcontextprotocol.io) somente-leitura para **licitações públicas brasileiras**. Conecta qualquer agente de IA (Claude, ChatGPT, Cursor, Hermes, agente próprio) às fontes oficiais de contratações públicas do Brasil, sem credencial e sem cadastro.

Fontes cobertas:

- **[PNCP](https://pncp.gov.br)** — Portal Nacional de Contratações Públicas (Lei 14.133/2021). Fonte nacional oficial.
- **[Compras.gov.br Dados Abertos](https://dadosabertos.compras.gov.br)** — catálogo federal: fornecedores, preços, atas de registro de preços, contratos, indicadores.

Os caminhos de API foram extraídos das especificações OpenAPI oficiais e validados ao vivo contra as duas fontes.

## O que ele faz

Descoberta, detalhamento e inteligência de preços. **Nenhuma ferramenta escreve, autentica ou submete proposta.** O servidor cobre a parte que a máquina faz bem; a decisão e o lance continuam com a pessoa.

## Instalação

```bash
pip install git+https://github.com/cYoren/licitacoes-mcp
```

Ou direto do código:

```bash
git clone https://github.com/cYoren/licitacoes-mcp
cd licitacoes-mcp
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

### Hermes Agent

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  licitacoes:
    command: licitacoes-mcp
```

### Claude Desktop / Cursor / qualquer cliente MCP

```json
{
  "mcpServers": {
    "licitacoes": {
      "command": "licitacoes-mcp"
    }
  }
}
```

Transporte HTTP:

```bash
LICITACOES_MCP_TRANSPORT=streamable-http licitacoes-mcp
```

## Ferramentas

### Descoberta (PNCP)

| Ferramenta | Para que serve |
| --- | --- |
| `buscar_editais` | Pesquisa full-text nacional por tema. Ex.: "capacitação de profissionais de saúde". |
| `listar_contratacoes_publicadas` | Volume publicado em um período, por modalidade. |
| `listar_oportunidades_abertas` | Tudo que ainda aceita proposta até uma data. |
| `listar_contratos_publicados` | Contratos firmados em um período. |
| `listar_atas_registro_precos` | Atas publicadas: preço de referência do governo. |

### Detalhamento (PNCP)

| Ferramenta | Para que serve |
| --- | --- |
| `detalhar_contratacao` | Registro completo a partir de CNPJ + ano + sequencial. |
| `listar_itens_contratacao` | Itens, quantidades e valor unitário estimado. |
| `listar_arquivos_contratacao` | Edital, termo de referência e anexos, com link. |
| `listar_resultados_item` | Quem ganhou e por quanto. |

### Inteligência (Compras.gov.br)

| Ferramenta | Para que serve |
| --- | --- |
| `consultar_fornecedor` | Cadastro federal de fornecedores por CNPJ. |
| `pesquisar_preco` | Preços praticados de material no catálogo federal. |
| `consultar_contratos_orgao` | Histórico contratual de um órgão federal. |
| `listar_arp_vigentes` | Atas de registro de preços federais vigentes. |
| `indicadores_compras` | Indicadores consolidados de compras federais. |
| `listar_modalidades` | Códigos de modalidade usados pelas outras ferramentas. |

## Fluxo típico

1. `buscar_editais(termo="seu produto")` para achar oportunidades por tema.
2. `detalhar_contratacao(cnpj, ano, sequencial)` e `listar_itens_contratacao(...)` para entender o objeto real.
3. `listar_arquivos_contratacao(...)` para ler o edital.
4. `listar_atas_registro_precos(...)` ou `pesquisar_preco(...)` para calibrar preço.
5. `listar_resultados_item(...)` para ver quem venceu e a quanto.

## Notas de engenharia

- `tamanhoPagina` mínimo de 10: as duas fontes rejeitam valores menores. O servidor corrige automaticamente.
- Retry com backoff em 429 e 5xx, cache TTL curto, User-Agent identificado.
- Datas em ISO 8601 (`YYYY-MM-DD`); a conversão para o formato interno do PNCP é feita pelo servidor.
- Valores monetários em BRL.
- Somente leitura: nenhuma operação `POST`, `PUT`, `PATCH` ou `DELETE` é usada nas fontes.

## Testes

```bash
pytest                      # inclui testes de rede contra as APIs reais
pytest -m "not live"        # só os testes offline
```

## Aviso

Projeto independente, sem vínculo com o governo federal. Os dados são públicos e de responsabilidade dos órgãos emissores. Confirme sempre no edital original antes de qualquer decisão — este servidor acelera a descoberta, não substitui a leitura do documento.

## Licença

MIT. Veja [LICENSE](LICENSE).
