"""
Módulo de normalização.

Responsável por transformar representações "sujas" de dinheiro e datas em
tipos nativos (float / datetime) que podem ser usados em cálculos.

Regra de ouro: o valor numérico interno é sempre um número.
A formatação (R$ 80.000,00) é responsabilidade exclusiva da apresentação.
"""

import re
import warnings
import pandas as pd

# Símbolos de moeda que devem ser removidos antes da conversão numérica.
SIMBOLOS_MOEDA = ["R$", "US$", "€", "£", "$"]


def normalizar_valor_monetario(series: pd.Series) -> pd.Series:
    """
    Converte uma coluna com valores monetários em diferentes formatos
    (BR, US, com ou sem símbolo) para uma série numérica (float).

    Aceita, entre outros:
        "R$ 80.000,00" -> 80000.0
        "80000,00"      -> 80000.0
        "80.000,00"     -> 80000.0
        "80000.00"      -> 80000.0
        "$80,000.00"    -> 80000.0
        "€ 80.000,00"   -> 80000.0

    Valores que não puderem ser convertidos viram NaN (nunca quebram o
    programa).
    """

    def _limpar(valor):
        if pd.isna(valor):
            return None

        texto = str(valor).strip()

        if texto == "":
            return None

        for simbolo in SIMBOLOS_MOEDA:
            texto = texto.replace(simbolo, "")

        texto = texto.strip()

        tem_virgula = "," in texto
        tem_ponto = "." in texto

        if tem_virgula and tem_ponto:
            # Formato brasileiro: 80.000,00  -> separador decimal é a vírgula
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            # Formato americano: 80,000.00  -> separador decimal é o ponto
            else:
                texto = texto.replace(",", "")
        elif tem_virgula:
            # Só vírgula: assume que é o separador decimal (padrão BR)
            texto = texto.replace(".", "").replace(",", ".")
        # Só ponto (ou nenhum separador): já está em formato numérico válido

        texto = re.sub(r"[^0-9.\-]", "", texto)

        return texto if texto not in ("", "-", ".") else None

    limpos = series.apply(_limpar)

    return pd.to_numeric(limpos, errors="coerce")


def normalizar_percentual(series: pd.Series) -> pd.Series:
    """
    Converte percentuais textuais ("5%", "5,5%") em números (5.0, 5.5).
    Não divide por 100 -- mantém a escala "porcentagem" (0-100), já que é
    assim que costuma ser exibido/comparado nos gráficos.
    """

    limpo = (
        series.astype(str)
        .str.strip()
        .str.replace("%", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(limpo, errors="coerce")


# Formatos de data mais comuns que o sistema deve reconhecer, em ordem de
# tentativa. Usar formatos explícitos evita o warning do Pandas
# ("Could not infer format") e acelera a conversão.
FORMATOS_DATA = [
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%m-%d-%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%b %d %Y",
    "%B %d %Y",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
]


def normalizar_data(series: pd.Series):
    """
    Converte uma coluna de datas em diferentes formatos para datetime.

    Retorna uma tupla (datas_convertidas, quantidade_invalida):
        - datas_convertidas: pd.Series de datetime64, com NaT nos valores
          que não puderam ser convertidos.
        - quantidade_invalida: quantos valores não puderam ser convertidos
          (ignorando valores originalmente vazios).
    """

    texto = series.astype(str).str.strip()

    melhor_resultado = None
    melhor_taxa_sucesso = -1

    for formato in FORMATOS_DATA:
        tentativa = pd.to_datetime(texto, format=formato, errors="coerce")
        taxa_sucesso = tentativa.notna().mean()

        if taxa_sucesso > melhor_taxa_sucesso:
            melhor_taxa_sucesso = taxa_sucesso
            melhor_resultado = tentativa

        if taxa_sucesso >= 0.99:
            break

    # Se nenhum formato explícito funcionou bem, tenta o parser genérico
    # do Pandas como última alternativa.
    if melhor_taxa_sucesso < 0.8:
        with warnings.catch_warnings():
            # A coluna pode nem ser uma data de verdade (o detector testa
            # todas as colunas) -- o parser genérico do Pandas avisa sobre
            # isso, mas o resultado já é tratado com errors="coerce".
            warnings.simplefilter("ignore", UserWarning)
            tentativa_generica = pd.to_datetime(
                texto, errors="coerce", dayfirst=True
            )
        if tentativa_generica.notna().mean() > melhor_taxa_sucesso:
            melhor_resultado = tentativa_generica
            melhor_taxa_sucesso = tentativa_generica.notna().mean()

    invalidos_originais = series.notna() & series.astype(str).str.strip().ne("")
    quantidade_invalida = int(
        (invalidos_originais & melhor_resultado.isna()).sum()
    )

    return melhor_resultado, quantidade_invalida
