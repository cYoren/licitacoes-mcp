"""Testes de construção de URL e normalização. Não tocam a rede."""

from licitacoes_mcp import sources
from licitacoes_mcp.client import page_size


def test_iso_to_compact():
    assert sources.iso_to_compact("2026-10-07") == "20261007"


def test_page_size_respeita_minimo_das_fontes():
    # PNCP e Compras.gov.br rejeitam tamanhoPagina < 10.
    assert page_size(1) == 10
    assert page_size(0) == 10
    assert page_size(50) == 50
    assert page_size(9999) == 500


def test_buscar_editais_monta_parametros():
    url, params = sources.url_buscar_editais("saude", "recebendo_proposta", "-data", 2, 10)
    assert url == "https://pncp.gov.br/api/search/"
    assert params["q"] == "saude"
    assert params["tipos_documento"] == "edital"
    assert params["pagina"] == 2
    assert params["tamanhoPagina"] == 10


def test_contratacoes_publicadas_usa_data_compacta():
    _, params = sources.url_contratacoes_publicadas("2026-10-01", "2026-10-07", 6, 1, 10)
    assert params["dataInicial"] == "20261001"
    assert params["dataFinal"] == "20261007"
    assert params["codigoModalidadeContratacao"] == 6


def test_urls_de_detalhe():
    assert sources.url_contratacao("123", 2026, 5).endswith("/api/consulta/v1/orgaos/123/compras/2026/5")
    assert sources.url_itens("123", 2026, 5).endswith("/api/pncp/v1/orgaos/123/compras/2026/5/itens")
    assert sources.url_resultados("123", 2026, 5, 2).endswith("/itens/2/resultados")


def test_envelope_uniformiza_data_e_items():
    a = sources.envelope({"data": [{"x": 1}], "totalRegistros": 7}, 1, 10)
    b = sources.envelope({"items": [{"y": 2}], "total": 3}, 1, 10)
    assert a["total"] == 7 and a["resultados"] == [{"x": 1}]
    assert b["total"] == 3 and b["resultados"] == [{"y": 2}]


def test_envelope_trata_204_e_lista_pura():
    vazio = sources.envelope(None, 1, 10)
    assert vazio["total"] == 0 and vazio["resultados"] == []
    lista = sources.envelope([{"a": 1}, {"a": 2}], 1, 10)
    assert lista["total"] == 2


def test_link_pncp_usa_rota_do_portal():
    # /compras/... responde 404; a rota real do PNCP é /app/editais/...
    assert sources.link_pncp("123", 2026, 5) == "https://pncp.gov.br/app/editais/123/2026/5"
    assert sources.link_pncp(None, 2026, 5) == sources.PNCP


def test_resumir_edital_extrai_campos_de_triagem():
    r = sources.resumir_edital({
        "numero_controle_pncp": "18291377000102-1-000192/2026",
        "title": "Edital nº PE 43/2026",
        "description": "Aquisição de equipamentos",
        "orgao_nome": "MUNICIPIO DE CARMO DO CAJURU",
        "orgao_cnpj": "18291377000102",
        "ano": "2026",
        "numero_sequencial": "192",
        "uf": "MG",
        "valor_total_estimado": 743520.22,
        "item_url": "/compras/18291377000102/2026/192",
    })
    assert r["uf"] == "MG"
    assert r["valor_total_estimado"] == 743520.22
    assert r["link_pncp"] == "https://pncp.gov.br/app/editais/18291377000102/2026/192"


def test_resumir_contratacao_achata_orgao():
    r = sources.resumir_contratacao({
        "orgaoEntidade": {"razaoSocial": "PREFEITURA X", "cnpj": "1"},
        "unidadeOrgao": {"ufSigla": "SP", "municipioNome": "Campinas"},
        "objetoCompra": "Merenda",
        "anoCompra": 2026,
        "sequencialCompra": 9,
    })
    assert r["orgao"] == "PREFEITURA X"
    assert r["uf"] == "SP"
    assert r["objeto"] == "Merenda"
    assert r["link_pncp"] == "https://pncp.gov.br/app/editais/1/2026/9"
