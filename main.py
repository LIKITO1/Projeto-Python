import pandas as pd
import streamlit as st
from analise import analisar_dados
from graficos import (
    grafico_marcas,
    grafico_vendas_mes,
    grafico_receita_marca,
    grafico_participacao_marca,
    grafico_comissao_vendedores,
    grafico_receita_mes
)
resultado=analisar_dados()
tabela=grafico_comissao_vendedores(resultado["vendedores"])
aba1,aba2,aba3=st.tabs([
    "Marcas",
    "Vendedores",
    "Receita por Mês"
])
with aba1:
    st.title("Dashboard de Vendas de Veículos")
    col1,col2,col3=st.columns([2,1,2])
    col1.write(f"Receita Total: R${resultado["receita_total"]:,.2f}")
    col2.write(f"Quantidade de Vendas: {resultado["quantidade_vendas"]}")
    col3.write(f"Valor Médio das Vendas: R${resultado["valor_medio_vendas"]:,.2f}")
    st.subheader("Gráfico de Receita por Marca")
    st.plotly_chart(grafico_receita_marca(resultado["receita_marca"]))
with aba2:
    st.title("Comissão dos Vendedores")
    st.dataframe(tabela,hide_index=True)
with aba3:
    st.title("Receita por Mês")
    st.plotly_chart(grafico_receita_mes(resultado["data_vendas"]),width="stretch")