"""
Indicadores gerais do dashboard.

Diferente da versão antiga (que dependia de nomes fixos como
"Sale_Price" ou "Car_Make"), estas funções recebem o mapeamento
semântico e só calculam um indicador quando as colunas necessárias
foram encontradas no CSV. Nenhum indicador é inventado.
"""

import pandas as pd

from normalizacao import normalizar_valor_monetario


def _coluna(mapeamento, tipo):
    if tipo not in mapeamento:
        return None
    return mapeamento[tipo]["coluna"]


def calcular_indicadores(df: pd.DataFrame, mapeamento: dict) -> dict:
    """
    Calcula indicadores gerais a partir do que estiver disponível no
    mapeamento. Cada chave só é incluída no resultado se puder ser
    calculada com os dados existentes.
    """

    indicadores = {
        "quantidade_registros": int(len(df))
    }

    coluna_valor = _coluna(mapeamento, "valor")
    if coluna_valor is not None:
        valores = normalizar_valor_monetario(df[coluna_valor]).dropna()
        if not valores.empty:
            indicadores["receita_total"] = float(valores.sum())
            indicadores["ticket_medio"] = float(valores.mean())

    coluna_comissao = _coluna(mapeamento, "comissao")
    if coluna_comissao is not None:
        comissoes = normalizar_valor_monetario(df[coluna_comissao]).dropna()
        if not comissoes.empty:
            indicadores["comissao_total"] = float(comissoes.sum())

    coluna_avaliacao = _coluna(mapeamento, "avaliacao")
    if coluna_avaliacao is not None:
        avaliacoes = pd.to_numeric(
            df[coluna_avaliacao], errors="coerce"
        ).dropna()
        if not avaliacoes.empty:
            indicadores["media_avaliacoes"] = float(avaliacoes.mean())

    coluna_marca = _coluna(mapeamento, "marca")
    if coluna_marca is not None:
        contagem = df[coluna_marca].dropna().value_counts()
        if not contagem.empty:
            indicadores["marca_mais_frequente"] = str(contagem.idxmax())

    coluna_estado = _coluna(mapeamento, "estado")
    if coluna_estado is not None:
        contagem = df[coluna_estado].dropna().value_counts()
        if not contagem.empty:
            indicadores["estado_com_mais_registros"] = str(contagem.idxmax())

    return indicadores
