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
        title="Participação de Cada Marca nas Vendas"
    )
    fig.show()
def grafico_comissao_vendedores(comisssao_vendedores):
    tabela=pd.DataFrame({
        "Vendedor":list(comisssao_vendedores.keys()),
        "Comissao":list(comisssao_vendedores.values())
    })
    tabela=tabela.sort_values(
        by="Comissao",
        ascending=False
    )
    tabela["Comissao"] = tabela["Comissao"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    return tabela
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
        title="Evolução das Vendas",
        markers=True
    )
    return fig