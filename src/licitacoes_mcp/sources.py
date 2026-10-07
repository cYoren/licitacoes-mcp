"""Endpoints e normalização das duas fontes públicas usadas pelo servidor.

PNCP  - Portal Nacional de Contratações Públicas (Lei 14.133/2021), fonte
        nacional oficial. Sem autenticação.
Compras.gov.br - Dados Abertos do compras.gov.br, catálogo federal
        (fornecedores, preços, ARP, contratos, indicadores). Sem autenticação.

Os caminhos abaixo foram extraídos das especificações OpenAPI oficiais:
  https://pncp.gov.br/pncp-api/v3/api-docs
  https://dadosabertos.compras.gov.br/v3/api-docs
e validados ao vivo. Ver ``tests/test_live.py``.
"""

from __future__ import annotations

from datetime import date
from typing import Any

PNCP = "https://pncp.gov.br"
COMPRAS = "https://dadosabertos.compras.gov.br"

MODALIDADES: dict[int, str] = {
    1: "Leilao - Eletronico",
    2: "Dialogo Competitivo",
    3: "Concurso",
    4: "Concorrencia - Eletronica",
    5: "Concorrencia - Presencial",
    6: "Pregao - Eletronico",
    7: "Pregao - Presencial",
    8: "Dispensa",
    9: "Inexigibilidade",
    10: "Manifestacao de Interesse",
    11: "Pre-qualificacao",
    12: "Credenciamento",
    13: "Leilao - Presencial",
}


def iso_to_compact(value: str) -> str:
    """``2026-10-07`` -> ``20261007`` (formato exigido pela consulta do PNCP)."""
    return date.fromisoformat(value).strftime("%Y%m%d")


def _pagination(pagina: int, tamanho_pagina: int) -> dict[str, int]:
    from .client import page_size

    return {"pagina": max(1, int(pagina)), "tamanhoPagina": page_size(tamanho_pagina)}


# --------------------------------------------------------------------------- #
# PNCP
# --------------------------------------------------------------------------- #

def url_buscar_editais(termo: str, status: str | None, ordenacao: str, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{PNCP}/api/search/", {
        "q": termo,
        "tipos_documento": "edital",
        "status": status,
        "ordenacao": ordenacao,
        **_pagination(pagina, tamanho_pagina),
    }


def url_contratacoes_publicadas(data_inicial: str, data_final: str, modalidade: int, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{PNCP}/api/consulta/v1/contratacoes/publicacao", {
        "dataInicial": iso_to_compact(data_inicial),
        "dataFinal": iso_to_compact(data_final),
        "codigoModalidadeContratacao": modalidade,
        **_pagination(pagina, tamanho_pagina),
    }


def url_oportunidades_abertas(data_final: str, modalidade: int, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{PNCP}/api/consulta/v1/contratacoes/proposta", {
        "dataFinal": iso_to_compact(data_final),
        "codigoModalidadeContratacao": modalidade,
        **_pagination(pagina, tamanho_pagina),
    }


def url_contratacao(cnpj: str, ano: int, sequencial: int) -> str:
    return f"{PNCP}/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}"


def url_itens(cnpj: str, ano: int, sequencial: int) -> str:
    return f"{PNCP}/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"


def url_arquivos(cnpj: str, ano: int, sequencial: int) -> str:
    return f"{PNCP}/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/arquivos"


def url_resultados(cnpj: str, ano: int, sequencial: int, numero_item: int) -> str:
    return f"{PNCP}/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numero_item}/resultados"


def url_contratos(data_inicial: str, data_final: str, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{PNCP}/api/consulta/v1/contratos", {
        "dataInicial": iso_to_compact(data_inicial),
        "dataFinal": iso_to_compact(data_final),
        **_pagination(pagina, tamanho_pagina),
    }


def url_atas(data_inicial: str, data_final: str, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{PNCP}/api/consulta/v1/atas", {
        "dataInicial": iso_to_compact(data_inicial),
        "dataFinal": iso_to_compact(data_final),
        **_pagination(pagina, tamanho_pagina),
    }


# --------------------------------------------------------------------------- #
# Compras.gov.br
# --------------------------------------------------------------------------- #

def url_fornecedor(cnpj: str | None, ativo: bool, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{COMPRAS}/modulo-fornecedor/1_consultarFornecedor", {
        "cnpj": cnpj,
        "ativo": str(ativo).lower(),
        **_pagination(pagina, tamanho_pagina),
    }


def url_pesquisa_preco(tipo: str, codigo: str, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{COMPRAS}/modulo-pesquisa-preco/1_consultarMaterial", {
        "tipo": tipo,
        "codigo": codigo,
        **_pagination(pagina, tamanho_pagina),
    }


def url_contratos_orgao(codigo_orgao: str, vigencia_inicial_min: str, vigencia_inicial_max: str, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{COMPRAS}/modulo-contratos/1_consultarContratos", {
        "codigoOrgao": codigo_orgao,
        "dataVigenciaInicialMin": vigencia_inicial_min,
        "dataVigenciaInicialMax": vigencia_inicial_max,
        **_pagination(pagina, tamanho_pagina),
    }


def url_arp(vigencia_inicial_min: str, vigencia_inicial_max: str, pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{COMPRAS}/modulo-arp/1_consultarARP", {
        "dataVigenciaInicialMin": vigencia_inicial_min,
        "dataVigenciaInicialMax": vigencia_inicial_max,
        **_pagination(pagina, tamanho_pagina),
    }


def url_indicadores(pagina: int, tamanho_pagina: int) -> tuple[str, dict[str, Any]]:
    return f"{COMPRAS}/modulo-indicadores/1_consultarIndicadoresConsolidados", _pagination(pagina, tamanho_pagina)


# --------------------------------------------------------------------------- #
# Normalização
# --------------------------------------------------------------------------- #

def envelope(data: Any, pagina: int, tamanho_pagina: int) -> dict[str, Any]:
    """Uniformiza a paginação das duas fontes."""
    if data is None:
        return {"pagina": pagina, "tamanho_pagina": tamanho_pagina, "total": 0, "resultados": []}

    if isinstance(data, list):
        resultados = data
        total = len(data)
    else:
        resultados = data.get("data") or data.get("resultado") or data.get("items") or []
        total = (
            data.get("totalRegistros")
            or data.get("total")
            or data.get("totalItems")
            or len(resultados)
        )

    return {
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total": total,
        "resultados": resultados,
    }


def link_pncp(cnpj: str | None, ano: object, sequencial: object) -> str:
    """URL pública de uma contratação no PNCP.

    A rota do portal é ``/app/editais/{cnpj}/{ano}/{sequencial}``. O índice de
    busca devolve ``item_url`` como ``/compras/...``, que responde 404, então a
    URL é sempre reconstruída a partir dos campos em vez de copiada.
    """
    if cnpj and ano and sequencial:
        return f"{PNCP}/app/editais/{cnpj}/{ano}/{sequencial}"
    return PNCP


def resumir_edital(item: dict[str, Any]) -> dict[str, Any]:
    """Versão enxuta de um resultado da busca textual do PNCP.

    O índice de busca devolve ~90 campos por documento; quase todos são ruído
    para triagem. Aqui ficam só os que decidem se vale abrir o edital.
    """
    return {
        "numero_controle_pncp": item.get("numero_controle_pncp"),
        "titulo": item.get("title"),
        "objeto": item.get("description"),
        "orgao": item.get("orgao_nome"),
        "cnpj": item.get("orgao_cnpj"),
        "esfera": item.get("esfera_nome"),
        "uf": item.get("uf"),
        "municipio": item.get("municipio_nome"),
        "modalidade": item.get("modalidade_licitacao_nome"),
        "situacao": item.get("situacao_nome"),
        "valor_total_estimado": item.get("valor_total_estimado"),
        "registro_de_precos": item.get("srp"),
        "data_publicacao": item.get("data_publicacao_pncp"),
        "recebimento_propostas_inicio": item.get("data_inicio_recebimento_propostas"),
        "recebimento_propostas_fim": item.get("data_fim_recebimento_propostas"),
        "ano": item.get("ano"),
        "sequencial": item.get("numero_sequencial"),
        "link_pncp": link_pncp(item.get("orgao_cnpj"), item.get("ano"), item.get("numero_sequencial")),
    }


def resumir_contratacao(item: dict[str, Any]) -> dict[str, Any]:
    """Versão enxuta de uma contratação, boa para triagem.

    O endpoint de consulta devolve a unidade em ``unidadeOrgao``; em alguns
    registros antigos o campo ``unidadeAdministrativa`` vem nulo, então os dois
    são aceitos.
    """
    orgao = item.get("orgaoEntidade") or {}
    unidade = item.get("unidadeOrgao") or item.get("unidadeAdministrativa") or {}
    return {
        "numero_controle_pncp": item.get("numeroControlePNCP"),
        "orgao": orgao.get("razaoSocial"),
        "cnpj": orgao.get("cnpj"),
        "uf": unidade.get("ufSigla"),
        "municipio": unidade.get("municipioNome"),
        "modalidade": item.get("modalidadeNome"),
        "situacao": item.get("situacaoCompraNome"),
        "objeto": item.get("objetoCompra"),
        "valor_total_estimado": item.get("valorTotalEstimado"),
        "data_abertura_proposta": item.get("dataAberturaProposta"),
        "data_encerramento_proposta": item.get("dataEncerramentoProposta"),
        "data_publicacao": item.get("dataPublicacaoPncp"),
        "link_pncp": link_pncp(orgao.get("cnpj"), item.get("anoCompra"), item.get("sequencialCompra")),
        "ano": item.get("anoCompra"),
        "sequencial": item.get("sequencialCompra"),
    }
