"""Testes de fumaça contra as APIs públicas reais.

Requerem rede. Rodam por padrão; use ``pytest -m "not live"`` para pular.
"""

import pytest

from licitacoes_mcp import server as S

pytestmark = pytest.mark.live


def _ok(dados):
    assert isinstance(dados, dict)
    assert "total" in dados and "resultados" in dados
    return dados


def test_buscar_editais_live():
    d = _ok(S.buscar_editais("capacitacao profissionais saude", tamanho_pagina=10))
    assert d["total"] > 0
    assert d["resultados"][0]["link_pncp"].startswith("https://pncp.gov.br")


def test_oportunidades_e_detalhe_live():
    d = _ok(S.listar_oportunidades_abertas("2026-10-20", tamanho_pagina=10))
    assert d["total"] > 0
    r = d["resultados"][0]
    detalhe = S.detalhar_contratacao(r["cnpj"], r["ano"], r["sequencial"])
    assert isinstance(detalhe, dict) and detalhe


def test_fornecedor_live():
    d = _ok(S.consultar_fornecedor(ativo=True, tamanho_pagina=10))
    assert d["total"] > 0


def test_modalidades_estatico():
    m = S.listar_modalidades()
    assert m[6] == "Pregao - Eletronico"
