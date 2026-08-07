import pandas as pd
import streamlit as st
from analise import analisar_dados
from datetime import datetime
from graficos import (
    grafico_marcas,
    grafico_vendas_mes,
    grafico_receita_marca,
    grafico_participacao_marca,
    grafico_comissao_vendedores,
    grafico_receita_mes,
    grafico_vendas_estado,
    grafico_avalicacoes
)
csv_usuario=st.file_uploader("Importe o CSV",type=["csv"])
if csv_usuario is not None:
    resultado=analisar_dados(csv_usuario)
else:
    st.info("Envie o CSV para receber o relatório")
    st.stop()
tabela=grafico_comissao_vendedores(resultado["vendedores"])
aba1,aba2,aba3,aba4,aba5,aba6=st.tabs([
    "Marcas",
    "Vendedores",
    "Evolução das Vendas",
    "Participação das Marcas",
    "Vendas por Estado",
    "Avaliações"
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
    st.title("Evolução das Vendas")
    st.plotly_chart(grafico_receita_mes(resultado["data_vendas"]),width="stretch")
with aba4:
    st.title("Participação das Marcas")
    st.plotly_chart(grafico_participacao_marca(resultado["marcas"]))
with aba5:
    st.title("Vendas por Estado")
    st.plotly_chart(grafico_vendas_estado(resultado["estados"]))
with aba6:
    st.title("Avaliações dos Clientes")
    st.plotly_chart(grafico_avalicacoes(resultado["avaliacoes"]))