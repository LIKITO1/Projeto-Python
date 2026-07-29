import pandas as pd
from limpeza import limpar_dados
from processamento import processar_dados
def analisar_dados():
    chunks=processar_dados()
    receita_total=0
    quantidade_vendas=0
    valor_medio_vendas=0
    num_clientes=set()
    comissao_total=0
    marcas={}
    modelos={}
    estados={}
    vendas_mes={}
    vendedores={}
    faturamento_mes={}
    satisfacao_total=0
    quantidade_avaliacoes=0
    avaliacoes=[]
    data_vendas={}
    receita_marca={}
    meses = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}
    for df in chunks:
        df=limpar_dados(df)
        df["Sale_Date"]=pd.to_datetime(df["Sale_Date"])
        df["Month"] = df["Sale_Date"].dt.month.map(meses)
        for marca,quantidade in df["Car_Make"].value_counts().items():
            if marca in marcas:
                marcas[marca]+=quantidade
            else:
                marcas[marca]=quantidade
        for modelo,quantidade in df["Car_Model"].value_counts().items():
            modelos[modelo]=modelos.get(modelo,0)+quantidade
        for estado,quantidade in df["State"].value_counts().items():
            estados[estado]=estados.get(estado,0)+quantidade
        for mes,quantidade in df["Month"].value_counts().items():
            vendas_mes[mes]=vendas_mes.get(mes,0)+quantidade
        for vendedor,valor in df.groupby("Salesperson")["Commission"].sum().items():
            vendedores[vendedor]=vendedores.get(vendedor,0)+valor
        for mes,valor in df.groupby("Month")["Sale_Price"].sum().items():
            faturamento_mes[mes]=faturamento_mes.get(mes,0)+valor
        for data,quantidade in df.groupby(df["Sale_Date"].dt.to_period("M")).size().items():
            data_vendas[str(data)]=data_vendas.get(str(data),0)+quantidade
        for marca,receita in df.groupby("Car_Make")["Sale_Price"].sum().items():
            receita_marca[marca]=receita_marca.get(marca,0)+receita
        avaliacoes.extend(df["Customer_Rating"].tolist())
        satisfacao_total+=df["Customer_Rating"].sum()
        quantidade_avaliacoes+=len(df)
        num_clientes.update(df["Customer_ID"])
        quantidade_vendas+=len(df)
        receita_total+=df["Sale_Price"].sum()
        comissao_total+=df["Commission"].sum()
    media_satisfacao=satisfacao_total/quantidade_avaliacoes
    media_mensal=sum(vendas_mes.values())/len(vendas_mes)
    valor_medio_vendas=receita_total/quantidade_vendas
    estado_com_mais_vendas=max(estados,key=estados.get)
    marca_mais_vendida=max(marcas,key=marcas.get)
    modelo_mais_vendido=max(modelos,key=modelos.get)
    return {
        "receita_total":receita_total,
        "quantidade_vendas":quantidade_vendas,
        "valor_medio_vendas":valor_medio_vendas,
        "num_clientes":num_clientes,
        "comissao_total":comissao_total,
        "marca_mais_vendida":marca_mais_vendida,
        "modelo_mais_vendido":modelo_mais_vendido,
        "estado_com_mais_vendas":estado_com_mais_vendas,
        "media_mensal":media_mensal,
        "vendas_mes":vendas_mes,
        "marcas":marcas,
        "modelos":modelos,
        "estados":estados,
        "vendedores":vendedores,
        "faturamento_mes":faturamento_mes,
        "media_satisfacao":media_satisfacao,
        "avaliacoes":avaliacoes,
        "data_vendas":data_vendas,
        "receita_marca":receita_marca,
    }