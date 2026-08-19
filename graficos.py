import plotly.express as px
import pandas as pd
def grafico_marcas(marcas):
    dados=pd.DataFrame({
        "Marca":list(marcas.keys()),
        "Vendas":list(marcas.values())
    })
    dados=dados.sort_values(
        by="Vendas",
        ascending=False
    )
    fig = px.bar(
        dados,
        x="Marca",
        y="Vendas",
        color="Marca"
    )
    fig.update_traces(
        texttemplate="%{y}",
        textposition="outside"
    )
    fig.update_yaxes(
        range=[
            dados["Vendas"].min()*0.9,
            dados["Vendas"].max()*1.1
        ]
    )
    return fig
def grafico_vendas_mes(vendas_mes):
    fig = px.line(
        x=list(vendas_mes.keys()),
        y=list(vendas_mes.values()),
        title="Receita mensal"
    )
    fig.show()
def grafico_receita_marca(receita_marca):
    dados=pd.DataFrame({
        "Marca":list(receita_marca.keys()),
        "Receita":list(receita_marca.values())
    })
    dados=dados.sort_values(
        by="Receita",
        ascending=False
    )
    fig=px.bar(
        dados,
        x="Marca",
        y="Receita",
        color="Marca"
    )
    return fig
def grafico_participacao_marca(marcas):
    participacao=pd.DataFrame({
        "Marca":marcas.keys(),
        "Vendas":marcas.values()
    })
    fig=px.pie(
        participacao,
        names="Marca",
        values="Vendas",
        color="Marca"
    )
    return fig
def tabela_comissao_vendedores(comissoes):
    """
    Monta uma tabela (não um gráfico) com a comissão de cada vendedor,
    já ordenada da maior para a menor e formatada como moeda por extenso.
    """

    from utils import formatar_moeda

    dados = pd.DataFrame({
        "Vendedor": list(comissoes.keys()),
        "Comissão": list(comissoes.values()),
    })

    dados = dados.sort_values(by="Comissão", ascending=False).reset_index(drop=True)
    dados["Comissão"] = dados["Comissão"].apply(formatar_moeda)

    return dados
def grafico_receita_mes(data_vendas):
    df = pd.DataFrame({
        "Data": list(data_vendas.keys()),
        "Vendas": list(data_vendas.values())
    })
    df["Data"] = pd.to_datetime(df["Data"])
    df = df.sort_values("Data")
    fig = px.line(
        df,
        x="Data",
        y="Vendas",
        markers=True
    )
    return fig
def grafico_vendas_estado(estados):
    dados=pd.DataFrame({
        "Estado":list(estados.keys()),
        "Vendas":list(estados.values())
    })
    dados=dados.sort_values(
        by="Vendas",
        ascending=False
    )
    fig=px.bar(
        dados,
        x="Estado",
        y="Vendas",
        color="Estado"
    )
    fig.update_yaxes(
        range=[
            dados["Vendas"].min()*0.9,
            dados["Vendas"].max()*1.1
        ]
    )
    return fig
def grafico_avalicacoes(avaliacoes):
    df = pd.DataFrame({
        "Avaliação": avaliacoes
    })
    df["Faixa"] = pd.cut(
        df["Avaliação"],
        bins=[1,1.5,2,2.5,3, 3.5, 4, 4.5, 5],
        labels=[
            "1.0 - 1.5",
            "1.5 - 2.0",
            "2.0 - 2.5",
            "2.5 - 3.0",
            "3.0 - 3.5",
            "3.5 - 4.0",
            "4.0 - 4.5",
            "4.5 - 5.0"
        ],
        include_lowest=True
    )
    contagem = (
        df["Faixa"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    contagem.columns = ["Faixa", "Quantidade"]
    fig = px.bar(
        contagem,
        x="Faixa",
        y="Quantidade",
        color="Faixa",
    )
    return fig