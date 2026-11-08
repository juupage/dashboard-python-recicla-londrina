
# --------------------------------------------------
# IMPORTAÇÃO DAS BIBLIOTECAS
# --------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Recicla Londrina | Data Analytics & Dashboard",
    page_icon="♻️",
    layout="wide"
)

# --------------------------------------------------
# CARREGAMENTO DOS DADOS
# --------------------------------------------------

@st.cache_data
def carregar_dados():
    df = pd.read_csv("indicadores_londrina_pr.csv")

    # Padronização dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Conversão do mês para data
    df["Data"] = pd.to_datetime(
        df["Mes"].astype(str) + "-01",
        errors="coerce"
    )

    return df


df = carregar_dados()

# --------------------------------------------------
# VALIDAÇÃO DAS COLUNAS
# --------------------------------------------------

colunas_necessarias = [
    "Municipio",
    "Mes",
    "Regiao_Setor",
    "Residuos_Urbanos_Coletados_ton",
    "Cobertura_Coleta_Urbana_pct",
    "Custo_Unitario_Urbana_R$_ton",
    "Residuos_Seletivos_Coletados_ton",
    "Taxa_Recuperacao_Seletiva_pct",
    "Rejeito_Coleta_Seletiva_pct",
    "Custo_Unitario_Seletiva_R$_ton",
    "Emissoes_CO2_Evitadas_t"
]

colunas_faltantes = [
    coluna for coluna in colunas_necessarias
    if coluna not in df.columns
]

if colunas_faltantes:
    st.error(
        f"Colunas não encontradas no CSV: {colunas_faltantes}"
    )
    st.stop()

# --------------------------------------------------
# BARRA LATERAL - FILTROS
# --------------------------------------------------

st.sidebar.title("♻️ Londrina Recicla")
st.sidebar.markdown("### Filtros de análise")

regioes = sorted(
    df["Regiao_Setor"].dropna().unique()
)

meses = sorted(
    df["Mes"].dropna().unique()
)

regioes_selecionadas = st.sidebar.multiselect(
    "Selecione as regiões:",
    options=regioes,
    default=regioes
)

meses_selecionados = st.sidebar.multiselect(
    "Selecione os meses:",
    options=meses,
    default=meses
)

# --------------------------------------------------
# FILTRAGEM DOS DADOS
# --------------------------------------------------

df_filtrado = df[
    (df["Regiao_Setor"].isin(regioes_selecionadas)) &
    (df["Mes"].isin(meses_selecionados))
].copy()

# --------------------------------------------------
# TÍTULO E APRESENTAÇÃO
# --------------------------------------------------

st.title("♻️ Dashboard de Gestão de Resíduos e Reciclagem")

st.markdown("""
Acompanhe os indicadores de coleta urbana, coleta seletiva,
recuperação de materiais recicláveis e impacto ambiental
no município de Londrina - PR.

Utilize os filtros laterais para explorar os resultados
por região e período.
""")

st.caption(
    "Base de dados simulada para fins acadêmicos e demonstrativos."
)

st.divider()

# --------------------------------------------------
# INDICADORES PRINCIPAIS (KPIs)
# --------------------------------------------------

st.subheader("Indicadores Gerais")

if not df_filtrado.empty:

    total_coleta_urbana = df_filtrado[
        "Residuos_Urbanos_Coletados_ton"
    ].sum()

    total_coleta_seletiva = df_filtrado[
        "Residuos_Seletivos_Coletados_ton"
    ].sum()

    total_recuperacao = df_filtrado[
        "Taxa_Recuperacao_Seletiva_pct"
    ].mean()

    co2_evitado = df_filtrado[
        "Emissoes_CO2_Evitadas_t"
    ].sum()

    maior_regiao_coleta = (
        df_filtrado.groupby("Regiao_Setor")[
            "Residuos_Urbanos_Coletados_ton"
        ].sum().idxmax()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Coleta Urbana",
        f"{total_coleta_urbana:,.0f} ton"
    )

    col2.metric(
        "Coleta Seletiva",
        f"{total_coleta_seletiva:,.0f} ton"
    )

    col3.metric(
        "Recuperação Média",
        f"{total_recuperacao:.2f}%"
    )

    col4.metric(
        "CO₂ Evitado",
        f"{co2_evitado:,.0f} ton"
    )

    col5.metric(
        "Maior Coleta Urbana",
        maior_regiao_coleta
    )

else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

st.divider()

# --------------------------------------------------
# ANÁLISES VISUAIS
# --------------------------------------------------

st.subheader("Análises Visuais")

if not df_filtrado.empty:

    # GRÁFICO 1 - COLETA POR REGIÃO

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:

        coleta_regiao = (
            df_filtrado.groupby("Regiao_Setor")[
                [
                    "Residuos_Urbanos_Coletados_ton",
                    "Residuos_Seletivos_Coletados_ton"
                ]
            ]
            .sum()
            .reset_index()
        )

        coleta_regiao = coleta_regiao.melt(
            id_vars="Regiao_Setor",
            var_name="Tipo de coleta",
            value_name="Quantidade (ton)"
        )

        grafico_coleta = px.bar(
            coleta_regiao,
            x="Regiao_Setor",
            y="Quantidade (ton)",
            color="Tipo de coleta",
            barmode="group",
            title="Coleta urbana x coleta seletiva por região"
        )

        grafico_coleta.update_layout(title_x=0.1)

        st.plotly_chart(
            grafico_coleta,
            use_container_width=True
        )

    # GRÁFICO 2 - EVOLUÇÃO MENSAL

    with col_graf2:

        evolucao_mensal = (
            df_filtrado.groupby("Data")[
                [
                    "Residuos_Urbanos_Coletados_ton",
                    "Residuos_Seletivos_Coletados_ton"
                ]
            ]
            .sum()
            .reset_index()
            .sort_values("Data")
        )

        evolucao_mensal = evolucao_mensal.melt(
            id_vars="Data",
            var_name="Tipo de coleta",
            value_name="Quantidade (ton)"
        )

        grafico_mensal = px.line(
            evolucao_mensal,
            x="Data",
            y="Quantidade (ton)",
            color="Tipo de coleta",
            markers=True,
            title="Evolução mensal da coleta de resíduos"
        )

        grafico_mensal.update_layout(title_x=0.1)

        st.plotly_chart(
            grafico_mensal,
            use_container_width=True
        )

    # GRÁFICO 3 - TAXA DE RECUPERAÇÃO

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:

        recuperacao_regiao = (
            df_filtrado.groupby("Regiao_Setor")[
                "Taxa_Recuperacao_Seletiva_pct"
            ]
            .mean()
            .reset_index()
        )

        grafico_recuperacao = px.bar(
            recuperacao_regiao,
            x="Regiao_Setor",
            y="Taxa_Recuperacao_Seletiva_pct",
            title="Taxa média de recuperação por região",
            labels={
                "Regiao_Setor": "Região",
                "Taxa_Recuperacao_Seletiva_pct": "Recuperação (%)"
            }
        )

        grafico_recuperacao.update_layout(title_x=0.1)

        st.plotly_chart(
            grafico_recuperacao,
            use_container_width=True
        )

    # GRÁFICO 4 - REJEITOS DA COLETA SELETIVA

    with col_graf4:

        rejeitos_regiao = (
            df_filtrado.groupby("Regiao_Setor")[
                "Rejeito_Coleta_Seletiva_pct"
            ]
            .mean()
            .reset_index()
        )

        grafico_rejeitos = px.bar(
            rejeitos_regiao,
            x="Regiao_Setor",
            y="Rejeito_Coleta_Seletiva_pct",
            title="Percentual de rejeitos por região",
            labels={
                "Regiao_Setor": "Região",
                "Rejeito_Coleta_Seletiva_pct": "Rejeitos (%)"
            }
        )

        grafico_rejeitos.update_layout(title_x=0.1)

        st.plotly_chart(
            grafico_rejeitos,
            use_container_width=True
        )

    # GRÁFICO 5 - IMPACTO AMBIENTAL

    col_graf5, col_graf6 = st.columns(2)

    with col_graf5:

        impacto_ambiental = (
            df_filtrado.groupby("Regiao_Setor")[
                "Emissoes_CO2_Evitadas_t"
            ]
            .sum()
            .reset_index()
        )

        grafico_co2 = px.pie(
            impacto_ambiental,
            names="Regiao_Setor",
            values="Emissoes_CO2_Evitadas_t",
            title="Distribuição de CO₂ evitado por região",
            hole=0.45
        )

        grafico_co2.update_traces(
            textinfo="percent+label"
        )

        grafico_co2.update_layout(title_x=0.1)

        st.plotly_chart(
            grafico_co2,
            use_container_width=True
        )

    # GRÁFICO 6 - CUSTO OPERACIONAL

    with col_graf6:

        custos_regiao = (
            df_filtrado.groupby("Regiao_Setor")[
                [
                    "Custo_Unitario_Urbana_R$_ton",
                    "Custo_Unitario_Seletiva_R$_ton"
                ]
            ]
            .mean()
            .reset_index()
        )

        custos_regiao = custos_regiao.melt(
            id_vars="Regiao_Setor",
            var_name="Tipo de coleta",
            value_name="Custo unitário (R$/ton)"
        )

        grafico_custos = px.bar(
            custos_regiao,
            x="Regiao_Setor",
            y="Custo unitário (R$/ton)",
            color="Tipo de coleta",
            barmode="group",
            title="Comparação do custo unitário por região"
        )

        grafico_custos.update_layout(title_x=0.1)

        st.plotly_chart(
            grafico_custos,
            use_container_width=True
        )

else:
    st.info("Selecione pelo menos uma região e um mês para visualizar os gráficos.")

# --------------------------------------------------
# TABELA DE DADOS DETALHADOS
# --------------------------------------------------

st.divider()

st.subheader("Dados Detalhados")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# DOWNLOAD DOS DADOS
# --------------------------------------------------

csv = df_filtrado.to_csv(
    index=False,
    sep=";",
    decimal=","
).encode("utf-8-sig")

st.download_button(
    label="📥 Baixar dados filtrados em CSV",
    data=csv,
    file_name="indicadores_londrina_filtrados.csv",
    mime="text/csv"
)

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------

st.divider()

st.caption(
    "Londrina Recicla | Projeto acadêmico de análise de dados "
    "e gestão de resíduos sólidos."
)
