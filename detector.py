import re
import unicodedata
import pandas as pd
from rapidfuzz import process, fuzz
from normalizacao import normalizar_data
# =========================================================
# PAPÉIS SEMÂNTICOS QUE O NOSSO SISTEMA CONSEGUE ENTENDER
# =========================================================
SINONIMOS = {
    "id": [
        "id",
        "codigo",
        "cod",
        "identificador",
        "id_cliente",
        "customer_id",
        "sale_id"
    ],
    "data": [
        "data",
        "date",
        "dia",
        "data_venda",
        "sale_date",
        "date_sale",
        "data_compra",
        "purchase_date"
    ],
    "valor": [
        "valor",
        "preco",
        "preço",
        "price",
        "valor_venda",
        "preco_venda",
        "preço_venda",
        "sale_price",
        "valor_total",
        "total",
        "receita",
        "revenue",
        "faturamento"
    ],
    "quantidade": [
        "quantidade",
        "qtd",
        "qtde",
        "quantity",
        "amount",
        "volume"
    ],
    "marca": [
        "marca",
        "fabricante",
        "brand",
        "make",
        "car_make"
    ],
    "modelo": [
        "modelo",
        "model",
        "car_model"
    ],
    "vendedor": [
        "vendedor",
        "vendedora",
        "salesperson",
        "seller",
        "consultor",
        "consultora",
        "representante",
        "sales_rep"
    ],
    "estado": [
        "estado",
        "uf",
        "state",
        "province",
        "regiao_estado"
    ],
    "cidade": [
        "cidade",
        "city",
        "municipio",
        "município"
    ],
    "pais": [
        "pais",
        "país",
        "country"
    ],
    "avaliacao": [
        "nota",
        "avaliacao",
        "avaliação",
        "rating",
        "score",
        "satisfacao",
        "satisfação"
    ],
    "porcentagem": [
        "percentual",
        "porcentagem",
        "percentage",
        "percent",
        "pct",
        "%",
        "taxa"
    ],
    "comissao": [
        "comissao",
        "comissão",
        "commission",
        "commission_value",
        "valor_comissao"
    ],
    "categoria": [
        "categoria",
        "category",
        "tipo",
        "type",
        "segmento",
        "segment"
    ],
    "combustivel": [
        "combustivel",
        "combustível",
        "fuel",
        "fuel_type",
        "tipo_combustivel"
    ],
    "transmissao": [
        "transmissao",
        "transmissão",
        "transmission",
        "cambio",
        "câmbio"
    ],
    "forma_pagamento": [
        "forma_pagamento",
        "pagamento",
        "payment",
        "payment_method",
        "metodo_pagamento",
        "método_pagamento"
    ]
}
TERMOS_PARA_TIPO = {
    termo: tipo
    for tipo, termos in SINONIMOS.items()
    for termo in termos
}
# =========================================================
# NORMALIZAÇÃO DO NOME
# =========================================================
def normalizar_nome(nome):
    nome = str(nome).strip().lower()
    # remove acentos
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(
        c for c in nome
        if not unicodedata.combining(c)
    )
    # troca separadores por espaço
    nome = re.sub(r"[_\-]+", " ", nome)
    # remove caracteres especiais
    nome = re.sub(r"[^a-z0-9 ]", " ", nome)
    # remove espaços duplicados
    nome = re.sub(r"\s+", " ", nome)
    return nome.strip()
# =========================================================
# DETECÇÃO POR NOME
# =========================================================
def detectar_por_nome(nome_coluna):
    nome = normalizar_nome(nome_coluna)
    melhor_tipo = None
    melhor_score = 0
    for tipo, termos in SINONIMOS.items():
        for termo in termos:
            termo_normalizado = normalizar_nome(termo)
            # Termos como "%" viram string vazia após a normalização (só
            # letras/números/espaço sobrevivem). Uma string vazia está
            # "contida" em qualquer nome, então ela precisa ser ignorada
            # para não gerar falsos positivos em toda coluna.
            if not termo_normalizado:
                continue
            # comparação direta
            if termo_normalizado == nome:
                return tipo, 100
            # termo contido no nome
            if termo_normalizado in nome:
                score = 95
                if score > melhor_score:
                    melhor_score = score
                    melhor_tipo = tipo
    # similaridade
    resultado = process.extractOne(
        nome,
        TERMOS_PARA_TIPO.keys(),
        scorer=fuzz.token_sort_ratio
    )
    if resultado:
        termo, score, _ = resultado
        if score >= 75:
            tipo = TERMOS_PARA_TIPO[termo]
            if score > melhor_score:
                melhor_score = score
                melhor_tipo = tipo
    if melhor_tipo is None:
        return None, 0
    return melhor_tipo, melhor_score
# =========================================================
# DETECÇÃO POR CONTEÚDO
# =========================================================
def detectar_por_conteudo(series):
    amostra = (
        series
        .dropna()
        .astype(str)
        .str.strip()
        .head(100)
    )
    if amostra.empty:
        return None, 0
    # -----------------------------------------------------
    # PORCENTAGEM
    # -----------------------------------------------------
    percentual = amostra.str.contains(
        r"%$",
        regex=True
    )
    if percentual.mean() >= 0.7:
        return "porcentagem", 95
    # -----------------------------------------------------
    # MOEDA
    # -----------------------------------------------------
    moeda = amostra.str.contains(
        r"R\$|US\$|€|\$|£",
        regex=True
    )
    if moeda.mean() >= 0.5:
        return "valor", 95
    datas, _invalidas = normalizar_data(amostra)
    proporcao_datas = datas.notna().mean()
    if proporcao_datas >= 0.8:
        return "data", 90
    numericos = pd.to_numeric(
        amostra.str.replace(
            ".",
            "",
            regex=False
        ).str.replace(
            ",",
            ".",
            regex=False
        ),
        errors="coerce"
    )
    proporcao_numerica = numericos.notna().mean()
    if proporcao_numerica >= 0.8:
        valores_validos = numericos.dropna()
        if not valores_validos.empty:
            unicos = series.nunique(
                dropna=True
            )
            total = len(series)
            proporcao_unicos = (
                unicos /
                max(total, 1)
            )
            if (
                proporcao_unicos > 0.95
                and
                (valores_validos % 1 == 0).mean() > 0.95
            ):
                return "id", 85
            if (
                valores_validos.min() >= 0
                and
                valores_validos.max() <= 5
                and
                valores_validos.nunique() <= 20
            ):
                return "avaliacao", 80
            if (
                (valores_validos % 1 == 0).mean() > 0.95
            ):
                return "quantidade", 70
            return "valor", 60
    proporcao_unicos = (
        series.nunique(dropna=True) /
        max(len(series), 1)
    )
    if proporcao_unicos < 0.2:
        return "categoria", 60
    return "texto", 50
def detectar_coluna(nome_coluna, series):
    tipo_nome, score_nome = detectar_por_nome(
        nome_coluna
    )
    tipo_conteudo, score_conteudo = detectar_por_conteudo(
        series
    )
    if tipo_nome and tipo_conteudo:
        if tipo_nome == tipo_conteudo:
            return {
                "tipo": tipo_nome,
                "confianca": min(
                    100,
                    int(
                        score_nome * 0.6
                        +
                        score_conteudo * 0.4
                    )
                )
            }
    if score_nome >= 90:
        return {
            "tipo": tipo_nome,
            "confianca": int(score_nome)
        }
    if tipo_conteudo:
        return {
            "tipo": tipo_conteudo,
            "confianca": int(score_conteudo)
        }
    return {
        "tipo": "texto",
        "confianca": 30
    }
def detectar_tipos_dataframe(df):
    resultado = {}
    for coluna in df.columns:
        resultado[coluna] = detectar_coluna(
            coluna,
            df[coluna]
        )
    return resultado