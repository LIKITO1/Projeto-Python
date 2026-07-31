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
resultado=analisar_dados()
tabela=grafico_comissao_vendedores(resultado["vendedores"])
aba1,aba2,aba3,aba4,aba5,aba6,aba7=st.tabs([
    "Marcas",
    "Vendedores",
    "Evolução das Vendas",
    "Participação das Marcas",
    "Vendas por Estado",
    "Avaliações",
    "Nova Venda"
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
with aba7:
    st.title("Nova Venda")
    with st.form("Cadastro"):
        data_venda=st.date_input("Data da Venda",datetime.now().date())
        vendedor=st.text_input("Nome do Vendedor")
        nome_cliente=st.text_input("Nome do Cliente")
        marca_carro=st.text_input("Nome da Marca")
        modelo_carro=st.text_input("Nome do Modelo")
        ano_carro=st.number_input(
            "Ano",
            min_value=1950,
            max_value=datetime.now().year,
            step=1
        )
        valor_venda=st.number_input(
        "Valor da Venda",
            min_value=0.0
        )
        desconto=st.number_input(
            "Desconto(%)",
            min_value=0.0
        )
        comissao=st.number_input(
            "Comissão do Vendedor(%)",
            min_value=0.0
        )
        estado=st.text_input("Estado(Exemplo:SP)")
        cidade=st.text_input("Cidade")
        metodo_pagamento=st.selectbox(
            "Método de Pagamento",
            ["Financiamento","Cartão de Débito","Cartão de Crédito"]
        )
        nota=st.slider(
            "Avaliação do Cliente",
            1.0,
            5.0,
            5.0,
            0.1
        )
        enviar=st.form_submit_button("Salvar Venda")