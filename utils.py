"""
Funções auxiliares que não pertencem a nenhuma camada específica
(detecção, mapeamento, geração de gráficos etc).
"""

import pandas as pd

ENCODINGS_TENTATIVAS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
SEPARADORES_TENTATIVAS = [",", ";", "\t", "|"]

def ler_csv_robusto(arquivo):
    """
    Tenta carregar um CSV enviado pelo usuário testando combinações comuns
    de encoding e separador, já que nem todo CSV vem em UTF-8 com vírgula.

    Retorna (df, encoding_usado, separador_usado).
    Lança ValueError se nenhuma combinação funcionar.
    """

    melhor_df = None
    melhor_encoding = None
    melhor_separador = None
    melhor_num_colunas = 0

    for encoding in ENCODINGS_TENTATIVAS:
        for separador in SEPARADORES_TENTATIVAS:
            try:
                arquivo.seek(0)
                df = pd.read_csv(
                    arquivo,
                    encoding=encoding,
                    sep=separador,
                    engine="python",
                )
            except Exception:
                continue

            # Um CSV lido com o separador errado normalmente vira uma
            # única coluna gigante. Preferimos a combinação que resulta em
            # mais colunas "de verdade".
            if df.shape[1] > melhor_num_colunas and df.shape[1] > 0:
                melhor_df = df
                melhor_encoding = encoding
                melhor_separador = separador
                melhor_num_colunas = df.shape[1]

            # Encontrou uma leitura com mais de uma coluna: já é um bom sinal.
            if melhor_num_colunas > 1:
                break
        if melhor_num_colunas > 1:
            break

    if melhor_df is None:
        raise ValueError(
            "Não foi possível ler o CSV. Verifique se o arquivo está "
            "íntegro e em um formato de texto separado por vírgula, "
            "ponto e vírgula ou tabulação."
        )

    return melhor_df, melhor_encoding, melhor_separador


# =========================================================
# Formatação de números para exibição
# (nunca abreviar/truncar o valor -- só formatar a apresentação)
# =========================================================

def formatar_moeda(valor: float) -> str:
    """
    Formata um número como moeda no padrão brasileiro, por extenso,
    sem abreviações (ex.: 1234567.8 -> "R$ 1.234.567,80").
    """

    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_numero(valor: float, casas_decimais: int = 0) -> str:
    """
    Formata um número no padrão brasileiro (separador de milhar com
    ponto), por extenso, sem abreviações (ex.: 12345 -> "12.345").
    """

    texto = f"{valor:,.{casas_decimais}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto
