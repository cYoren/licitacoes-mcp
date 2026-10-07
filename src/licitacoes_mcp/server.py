"""Servidor MCP de licitações públicas brasileiras.

Expõe as fontes oficiais (PNCP e Compras.gov.br Dados Abertos) como ferramentas
somente-leitura para agentes de IA. Nenhuma ferramenta escreve, autentica ou
submete proposta: o servidor cobre descoberta, detalhamento e inteligência de
preços. A decisão e o lance continuam com a pessoa.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.mcpserver import MCPServer

from . import sources
from .client import ApiClient

server = MCPServer(
    name="licitacoes-mcp",
    version="0.1.0",
    instructions=(
        "Ferramentas somente-leitura sobre licitações públicas brasileiras. "
        "Use 'buscar_editais' para pesquisa textual ampla, "
        "'listar_oportunidades_abertas' para o que ainda aceita proposta, "
        "'detalhar_contratacao' mais 'listar_itens_contratacao' para o objeto completo, "
        "e 'pesquisar_preco' / 'listar_atas_registro_precos' para preço de referência. "
        "Valores monetários estão em BRL. Datas seguem ISO 8601 (YYYY-MM-DD)."
    ),
)

_client = ApiClient()


def _get(url: str, params: dict[str, Any] | None = None) -> Any:
    return _client.get_json(url, params)


# --------------------------------------------------------------------------- #
# PNCP - descoberta
# --------------------------------------------------------------------------- #

@server.tool(description="Pesquisa editais e contratações por palavra-chave no PNCP (índice full-text nacional). Use para descobrir oportunidades por tema, ex.: 'capacitação de profissionais de saúde'.")
def buscar_editais(
    termo: str,
    status: str = "recebendo_proposta",
    ordenacao: str = "-data",
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_buscar_editais(termo, status, ordenacao, pagina, tamanho_pagina)
    dados = sources.envelope(_get(url, params), pagina, tamanho_pagina)
    dados["resultados"] = [sources.resumir_edital(i) for i in dados["resultados"]]
    return dados


@server.tool(description="Lista contratações publicadas no PNCP em um intervalo de datas, por modalidade. Sem filtro de tema: use para medir volume ou varrer um período. Modalidade 6 = Pregão Eletrônico.")
def listar_contratacoes_publicadas(
    data_inicial: str,
    data_final: str,
    modalidade: int = 6,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_contratacoes_publicadas(data_inicial, data_final, modalidade, pagina, tamanho_pagina)
    dados = sources.envelope(_get(url, params), pagina, tamanho_pagina)
    dados["resultados"] = [sources.resumir_contratacao(i) for i in dados["resultados"]]
    return dados


@server.tool(description="Lista contratações que ainda aceitam proposta até uma data limite. É a lista de oportunidades em aberto, já ordenável por prazo.")
def listar_oportunidades_abertas(
    data_final: str,
    modalidade: int = 6,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_oportunidades_abertas(data_final, modalidade, pagina, tamanho_pagina)
    dados = sources.envelope(_get(url, params), pagina, tamanho_pagina)
    dados["resultados"] = [sources.resumir_contratacao(i) for i in dados["resultados"]]
    return dados


# --------------------------------------------------------------------------- #
# PNCP - detalhamento
# --------------------------------------------------------------------------- #

@server.tool(description="Detalhe completo de uma contratação do PNCP a partir de CNPJ do órgão, ano e número sequencial. Esses três campos vêm em 'listar_oportunidades_abertas'.")
def detalhar_contratacao(cnpj: str, ano: int, sequencial: int) -> dict[str, Any]:
    return _get(sources.url_contratacao(cnpj, ano, sequencial))


@server.tool(description="Itens de uma contratação com descrição, quantidade, unidade e valor unitário estimado. É aqui que se vê o que o órgão realmente compra e por quanto estima pagar.")
def listar_itens_contratacao(cnpj: str, ano: int, sequencial: int) -> list[dict[str, Any]]:
    return _get(sources.url_itens(cnpj, ano, sequencial)) or []


@server.tool(description="Documentos de uma contratação (edital, termo de referência, anexos) com link de download. Geralmente PDF.")
def listar_arquivos_contratacao(cnpj: str, ano: int, sequencial: int) -> list[dict[str, Any]]:
    return _get(sources.url_arquivos(cnpj, ano, sequencial)) or []


@server.tool(description="Resultado homologado de um item: quem ganhou e por qual preço. Use para saber o preço praticado e o fornecedor vencedor de uma disputa encerrada.")
def listar_resultados_item(cnpj: str, ano: int, sequencial: int, numero_item: int) -> list[dict[str, Any]]:
    return _get(sources.url_resultados(cnpj, ano, sequencial, numero_item)) or []


# --------------------------------------------------------------------------- #
# PNCP - séries históricas
# --------------------------------------------------------------------------- #

@server.tool(description="Contratos públicos firmados no PNCP em um intervalo de datas. Serve para mapear quem já contrata o que você vende.")
def listar_contratos_publicados(
    data_inicial: str,
    data_final: str,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_contratos(data_inicial, data_final, pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


@server.tool(description="Atas de registro de preços publicadas no PNCP em um intervalo. Referência de preços já registrados por órgãos públicos, útil para calibrar proposta.")
def listar_atas_registro_precos(
    data_inicial: str,
    data_final: str,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_atas(data_inicial, data_final, pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


# --------------------------------------------------------------------------- #
# Compras.gov.br
# --------------------------------------------------------------------------- #

@server.tool(description="Consulta o cadastro de fornecedores do governo federal. Informe um CNPJ para ver a situação de um fornecedor específico, ou deixe vazio para listar fornecedores ativos.")
def consultar_fornecedor(
    cnpj: str | None = None,
    ativo: bool = True,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_fornecedor(cnpj, ativo, pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


@server.tool(description="Pesquisa de preços de materiais no catálogo federal. tipo='codigoItemCatalogo' ou 'codigoPdm' e codigo é o código do item. Devolve preços praticados em compras públicas.")
def pesquisar_preco(
    codigo: str,
    tipo: str = "codigoItemCatalogo",
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_pesquisa_preco(tipo, codigo, pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


@server.tool(description="Contratos de um órgão federal específico (codigoOrgao) vigentes em uma janela de datas. Mostra o histórico contratual daquele órgão.")
def consultar_contratos_orgao(
    codigo_orgao: str,
    vigencia_inicial_min: str,
    vigencia_inicial_max: str,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_contratos_orgao(codigo_orgao, vigencia_inicial_min, vigencia_inicial_max, pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


@server.tool(description="Atas de registro de preços federais vigentes em uma janela de datas, com link para a ata e para a compra no PNCP.")
def listar_arp_vigentes(
    vigencia_inicial_min: str,
    vigencia_inicial_max: str,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    url, params = sources.url_arp(vigencia_inicial_min, vigencia_inicial_max, pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


@server.tool(description="Indicadores consolidados de compras públicas federais. Visão agregada de volume e valores.")
def indicadores_compras(pagina: int = 1, tamanho_pagina: int = 10) -> dict[str, Any]:
    url, params = sources.url_indicadores(pagina, tamanho_pagina)
    return sources.envelope(_get(url, params), pagina, tamanho_pagina)


# --------------------------------------------------------------------------- #
# Referência
# --------------------------------------------------------------------------- #

@server.tool(description="Tabela de códigos de modalidade de contratação do PNCP. Consulte antes de passar 'modalidade' para as outras ferramentas.")
def listar_modalidades() -> dict[int, str]:
    return sources.MODALIDADES


def main() -> None:
    transport = os.environ.get("LICITACOES_MCP_TRANSPORT", "stdio")
    server.run(transport=transport)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
