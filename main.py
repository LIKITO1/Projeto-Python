import pandas as pd
import streamlit as st

from utils import ler_csv_robusto, formatar_moeda, formatar_numero
from detector import detectar_tipos_dataframe, SINONIMOS
from mapeamento import criar_mapeamento
from regras_graficos import descobrir_graficos_possiveis
from gerador_graficos import gerar_graficos_disponiveis
from validacao import validar_dataframe
from analise import calcular_indicadores

# =========================================================
# Configuração geral da página
# =========================================================
st.set_page_config(
    page_title="Analisador Inteligente de CSVs",
    page_icon="📊",
    layout="wide",
)

CONFIANCA_ACEITAR_AUTOMATICO = 85
CONFIANCA_MINIMA_AVISO = 60
MAX_CARDS_POR_LINHA = 3  # evita colunas estreitas que cortam números

ROTULOS_INDICADORES = {
    "quantidade_registros": ("Registros", "numero"),
    "receita_total": ("Receita total", "moeda"),
    "ticket_medio": ("Ticket médio", "moeda"),
    "comissao_total": ("Comissão total", "moeda"),
    "media_avaliacoes": ("Avaliação média", "decimal"),
    "marca_mais_frequente": ("Marca mais frequente", "texto"),
    "estado_com_mais_registros": ("Estado com mais registros", "texto"),
}


def formatar_indicador(chave, valor):
    _rotulo, tipo = ROTULOS_INDICADORES.get(chave, (chave, "texto"))
    if tipo == "moeda":
        return formatar_moeda(valor)
    if tipo == "numero":
        return formatar_numero(valor)
    if tipo == "decimal":
        return formatar_numero(valor, casas_decimais=2)
    return str(valor)


# =========================================================
# Barra lateral: upload e instruções
# =========================================================
with st.sidebar:
    st.title("📊 Analisador de CSVs")
    st.caption(
        "Envie um CSV com qualquer estrutura de colunas — o sistema "
        "identifica automaticamente o significado de cada coluna e "
        "gera os gráficos e indicadores compatíveis com os dados "
        "encontrados."
    )
    csv_usuario = st.file_uploader("Importe o CSV", type=["csv"])
    st.divider()
    st.caption(
        "💡 Nomes de coluna não precisam ser iguais aos originais. "
        "Ex.: 'Preço Final', 'Valor da Venda' e 'Sale_Price' são "
        "reconhecidos como o mesmo conceito."
    )

if csv_usuario is None:
    st.title("📊 Analisador Inteligente de CSVs")
    st.info("⬅️ Envie um CSV na barra lateral para começar.")
    st.stop()

try:
    df, encoding_usado, separador_usado = ler_csv_robusto(csv_usuario)
except ValueError as erro:
    st.error(str(erro))
    st.stop()

if df.empty:
    st.warning("O CSV enviado está vazio.")
    st.stop()

relatorio_validacao = validar_dataframe(df)
deteccoes = detectar_tipos_dataframe(df)

# =========================================================
# Cabeçalho com resumo do arquivo
# =========================================================
st.title("📊 Analisador Inteligente de CSVs")
st.caption(f"Arquivo: **{csv_usuario.name}**")

resumo1, resumo2, resumo3 = st.columns(3)
resumo1.metric("Linhas", formatar_numero(relatorio_validacao["total_linhas"]))
resumo2.metric("Colunas", formatar_numero(relatorio_validacao["total_colunas"]))
resumo3.metric("Linhas duplicadas", formatar_numero(relatorio_validacao["linhas_duplicadas"]))

st.divider()

# =========================================================
# Abas principais
# =========================================================
aba_visao_geral, aba_colunas, aba_graficos, aba_qualidade = st.tabs([
    "📈 Visão Geral",
    "🔍 Colunas Detectadas",
    "📊 Gráficos",
    "⚠️ Qualidade dos Dados",
])

# ---------------------------------------------------------
# Aba: Colunas Detectadas (com correção manual embutida)
# ---------------------------------------------------------
with aba_colunas:
    st.subheader("Colunas identificadas")
    st.caption(
        "Confira se o sistema interpretou corretamente cada coluna do "
        "seu CSV. Se alguma detecção estiver errada, corrija na coluna "
        "**'Corrigir para'** abaixo — os gráficos são recalculados "
        "automaticamente."
    )

    tipos_disponiveis = sorted(SINONIMOS.keys())
    opcoes_selectbox = ["(manter automático)", "Ignorar coluna"] + tipos_disponiveis

    def status_confianca(confianca):
        if confianca >= CONFIANCA_ACEITAR_AUTOMATICO:
            return "✅ Alta"
        if confianca >= CONFIANCA_MINIMA_AVISO:
            return "⚠️ Média"
        return "❓ Baixa"

    tabela_deteccoes = pd.DataFrame([
        {
            "Coluna original": coluna,
            "Significado detectado": resultado["tipo"],
            "Confiança": resultado["confianca"],
            "Status": status_confianca(resultado["confianca"]),
            "Corrigir para": "(manter automático)",
        }
        for coluna, resultado in deteccoes.items()
    ])

    tabela_editada = st.data_editor(
        tabela_deteccoes,
        column_config={
            "Confiança": st.column_config.ProgressColumn(
                "Confiança", min_value=0, max_value=100, format="%d%%"
            ),
            "Corrigir para": st.column_config.SelectboxColumn(
                "Corrigir para", options=opcoes_selectbox, required=True
            ),
        },
        disabled=["Coluna original", "Significado detectado", "Confiança", "Status"],
        hide_index=True,
        width="stretch",
        key="tabela_correcao_colunas",
    )

    overrides = {}
    for _, linha in tabela_editada.iterrows():
        escolha = linha["Corrigir para"]
        if escolha == "Ignorar coluna":
            overrides[linha["Coluna original"]] = None
        elif escolha != "(manter automático)":
            overrides[linha["Coluna original"]] = escolha

# Aplica as correções manuais do usuário por cima da detecção automática.
deteccoes_finais = {}
for coluna, resultado in deteccoes.items():
    if coluna in overrides:
        tipo_manual = overrides[coluna]
        if tipo_manual is None:
            continue
        deteccoes_finais[coluna] = {"tipo": tipo_manual, "confianca": 100}
    else:
        deteccoes_finais[coluna] = resultado

mapeamento = criar_mapeamento(deteccoes_finais)
graficos_possiveis = descobrir_graficos_possiveis(mapeamento)
graficos = gerar_graficos_disponiveis(df, mapeamento, graficos_possiveis)
indicadores = calcular_indicadores(df, mapeamento)

# ---------------------------------------------------------
# Aba: Visão Geral (indicadores em grade fixa, sem cortar números)
# ---------------------------------------------------------
with aba_visao_geral:
    if not indicadores:
        st.info("Nenhum indicador pôde ser calculado com os dados encontrados.")
    else:
        st.subheader("Indicadores gerais")
        itens = list(indicadores.items())
        for inicio in range(0, len(itens), MAX_CARDS_POR_LINHA):
            fatia = itens[inicio:inicio + MAX_CARDS_POR_LINHA]
            colunas_linha = st.columns(MAX_CARDS_POR_LINHA)
            for coluna_ui, (chave, valor) in zip(colunas_linha, fatia):
                rotulo, _tipo = ROTULOS_INDICADORES.get(chave, (chave, "texto"))
                coluna_ui.metric(rotulo, formatar_indicador(chave, valor))

    st.divider()
    st.subheader("Resumo dos gráficos")
    if not graficos_possiveis:
        st.warning(
            "Nenhum gráfico pôde ser identificado como possível com as "
            "colunas encontradas neste CSV."
        )
    else:
        gerados = set(graficos)
        for codigo, regra in graficos_possiveis.items():
            if codigo in gerados:
                st.write(f"✅ {regra['nome']}")
            else:
                st.write(f"⚪ {regra['nome']} — dados insuficientes após a limpeza")

# ---------------------------------------------------------
# Aba: Gráficos
# ---------------------------------------------------------
with aba_graficos:
    if not graficos:
        st.warning(
            "Não foi possível identificar dados suficientes neste CSV "
            "para gerar nenhum dos gráficos disponíveis no sistema."
        )
    else:
        nomes_abas = [graficos_possiveis[codigo]["nome"] for codigo in graficos]
        sub_abas = st.tabs(nomes_abas)
        for sub_aba, codigo in zip(sub_abas, graficos):
            with sub_aba:
                resultado = graficos[codigo]
                if isinstance(resultado, pd.DataFrame):
                    st.dataframe(resultado, hide_index=True, width="stretch")
                else:
                    st.plotly_chart(resultado, width="stretch")

# ---------------------------------------------------------
# Aba: Qualidade dos Dados
# ---------------------------------------------------------
with aba_qualidade:
    st.subheader("Qualidade dos dados")

    problemas_encontrados = (
        relatorio_validacao["linhas_duplicadas"]
        or relatorio_validacao["valores_ausentes_por_coluna"]
    )

    if not problemas_encontrados:
        st.success("Nenhum problema encontrado nos dados. ✅")
    else:
        if relatorio_validacao["linhas_duplicadas"]:
            st.warning(
                f"{formatar_numero(relatorio_validacao['linhas_duplicadas'])} "
                "linha(s) duplicada(s) no arquivo."
            )

        if relatorio_validacao["valores_ausentes_por_coluna"]:
            st.write("**Valores ausentes por coluna:**")
            tabela_ausentes = pd.DataFrame([
                {"Coluna": coluna, "Valores ausentes": formatar_numero(quantidade)}
                for coluna, quantidade in relatorio_validacao["valores_ausentes_por_coluna"].items()
            ])
            st.dataframe(tabela_ausentes, hide_index=True, width="stretch")

    graficos_nao_gerados = set(graficos_possiveis) - set(graficos)
    if graficos_nao_gerados:
        st.write("**Gráficos identificados como possíveis, mas sem dados válidos suficientes:**")
        for codigo in graficos_nao_gerados:
            st.write(f"- {graficos_possiveis[codigo]['nome']}")
