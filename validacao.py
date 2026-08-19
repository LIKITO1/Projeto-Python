"""
Módulo de validação.

Não impede a aplicação de funcionar: apenas identifica problemas nos
dados (valores ausentes, duplicatas, conversões que falharam) para que o
usuário seja informado, em vez do sistema quebrar silenciosamente.
"""

import pandas as pd


def validar_dataframe(df: pd.DataFrame) -> dict:
    """
    Faz uma checagem geral do DataFrame carregado.
    Retorna um relatório simples, sem alterar os dados.
    """

    linhas_duplicadas = int(df.duplicated().sum())

    valores_ausentes_por_coluna = {
        coluna: int(quantidade)
        for coluna, quantidade in df.isna().sum().items()
        if quantidade > 0
    }

    return {
        "total_linhas": int(len(df)),
        "total_colunas": int(len(df.columns)),
        "linhas_duplicadas": linhas_duplicadas,
        "valores_ausentes_por_coluna": valores_ausentes_por_coluna,
    }


def relatorio_conversao(nome_coluna: str, serie_original: pd.Series, serie_convertida: pd.Series) -> dict:
    """
    Compara uma coluna antes/depois de uma normalização (monetária,
    percentual ou de data) e informa quantos valores não puderam ser
    convertidos.

    Um valor originalmente vazio não conta como "inválido" -- ele
    simplesmente está ausente.
    """

    preenchidos_original = serie_original.notna() & serie_original.astype(str).str.strip().ne("")
    falharam = preenchidos_original & serie_convertida.isna()

    return {
        "coluna": nome_coluna,
        "total": int(len(serie_original)),
        "convertidos_com_sucesso": int((preenchidos_original & serie_convertida.notna()).sum()),
        "invalidos": int(falharam.sum()),
    }
