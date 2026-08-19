"""
Camada responsável por transformar as colunas reais do CSV (encontradas
através do mapeamento semântico) em dados prontos para os gráficos.

Regra fundamental: nenhuma função aqui acessa diretamente um nome de
coluna fixo como df["Sale_Price"]. Tudo passa pelo mapeamento.
"""

import pandas as pd

from graficos import (
    grafico_receita_marca,
    grafico_participacao_marca,
    grafico_receita_mes,
    grafico_vendas_estado,
    grafico_avalicacoes,
    tabela_comissao_vendedores,
)
from normalizacao import normalizar_valor_monetario, normalizar_data


def obter_coluna(mapeamento, tipo):
    """
    Retorna o nome real da coluna correspondente ao tipo semântico,
    ou None se esse tipo não foi encontrado no CSV.
    """

    if tipo not in mapeamento:
        return None

    return mapeamento[tipo]["coluna"]


def gerar_receita_por_marca(df, mapeamento):
    coluna_marca = obter_coluna(mapeamento, "marca")
    coluna_valor = obter_coluna(mapeamento, "valor")

    if coluna_marca is None or coluna_valor is None:
        return None

    valores = normalizar_valor_monetario(df[coluna_valor])

    dados = (
        pd.DataFrame({
            "marca": df[coluna_marca],
            "valor": valores,
        })
        .dropna()
        .groupby("marca")["valor"]
        .sum()
        .sort_values(ascending=False)
    )

    if dados.empty:
        return None

    return grafico_receita_marca(dados.to_dict())


def gerar_participacao_marcas(df, mapeamento):
    coluna_marca = obter_coluna(mapeamento, "marca")

    if coluna_marca is None:
        return None

    dados = df[coluna_marca].dropna().value_counts()

    if dados.empty:
        return None

    return grafico_participacao_marca(dados.to_dict())


def gerar_evolucao_vendas(df, mapeamento):
    coluna_data = obter_coluna(mapeamento, "data")

    if coluna_data is None:
        return None

    datas, _invalidas = normalizar_data(df[coluna_data])

    dados = (
        datas
        .dropna()
        .dt.to_period("M")
        .value_counts()
        .sort_index()
    )

    if dados.empty:
        return None

    dados = {
        str(periodo): int(quantidade)
        for periodo, quantidade in dados.items()
    }

    return grafico_receita_mes(dados)


def gerar_vendas_por_estado(df, mapeamento):
    coluna_estado = obter_coluna(mapeamento, "estado")

    if coluna_estado is None:
        return None

    dados = df[coluna_estado].dropna().value_counts()

    if dados.empty:
        return None

    return grafico_vendas_estado(dados.to_dict())


def gerar_avaliacoes(df, mapeamento):
    coluna_avaliacao = obter_coluna(mapeamento, "avaliacao")

    if coluna_avaliacao is None:
        return None

    dados = pd.to_numeric(
        df[coluna_avaliacao], errors="coerce"
    ).dropna()

    if dados.empty:
        return None

    return grafico_avalicacoes(dados.tolist())


def gerar_comissao_vendedores(df, mapeamento):
    coluna_vendedor = obter_coluna(mapeamento, "vendedor")
    coluna_comissao = obter_coluna(mapeamento, "comissao")

    if coluna_vendedor is None or coluna_comissao is None:
        return None

    comissoes = normalizar_valor_monetario(df[coluna_comissao])

    dados = (
        pd.DataFrame({
            "vendedor": df[coluna_vendedor],
            "comissao": comissoes,
        })
        .dropna()
        .groupby("vendedor")["comissao"]
        .sum()
        .sort_values(ascending=False)
    )

    if dados.empty:
        return None

    return tabela_comissao_vendedores(dados.to_dict())


# As chaves aqui devem ser EXATAMENTE as mesmas usadas em
# REGRAS_GRAFICOS (regras_graficos.py). Isso é o que permite que
# gerar_graficos_disponiveis() encontre o gerador certo para cada
# gráfico "descoberto" como possível.
GERADORES = {
    "receita_marca": gerar_receita_por_marca,
    "participacao_marca": gerar_participacao_marcas,
    "evolucao_vendas": gerar_evolucao_vendas,
    "vendas_estado": gerar_vendas_por_estado,
    "avaliacoes": gerar_avaliacoes,
    "comissao_vendedores": gerar_comissao_vendedores,
}


def gerar_graficos_disponiveis(df, mapeamento, graficos_possiveis):
    """
    Gera apenas os gráficos que:
      1. foram identificados como possíveis pelas regras (colunas
         necessárias existem no mapeamento), e
      2. realmente produziram dados válidos após a normalização.

    Nunca inventa dados: se um gerador retornar None, o gráfico
    simplesmente não aparece.
    """

    resultados = {}

    for codigo in graficos_possiveis:
        gerador = GERADORES.get(codigo)

        if gerador is None:
            continue

        figura = gerador(df, mapeamento)

        if figura is not None:
            resultados[codigo] = figura

    return resultados
