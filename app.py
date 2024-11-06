import streamlit as st
from card_generation import CartaoPrograma
from model_training import PrevisorCrime
from data_processing import CrimeData
from graphs import (
    create_hourly_crime_graph,
    create_neighborhood_crime_graph,
    create_weekday_crime_graph,
    create_crime_type_pareto_graph,
    create_crime_trend_graph,
    create_shift_crime_graph
)
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils import dias_da_semana
from datetime import datetime, time

# Configuração da página
st.set_page_config(page_title="Cartão Programa Automatizado", layout='wide')

# Aplicar estilo CSS
try:
    st.markdown(
        f"""
        <style>
        {open('style.css').read()}
        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning("Arquivo style.css não encontrado. Certifique-se de que o arquivo de estilo está no diretório correto.")

st.header('Sistema de Geração de Cartão Programa Automatizado')
st.sidebar.image('img/icon.png', caption='Cartão Programa Automatizado')

# Inicialização das variáveis de estado da sessão
if 'pontos_patrulhamento' not in st.session_state:
    st.session_state.pontos_patrulhamento = []
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'crime_data' not in st.session_state:
    st.session_state.crime_data = None
if 'excel_path' not in st.session_state:
    st.session_state.excel_path = None

# Definição das faixas horárias
faixas_horarias = [
    ("00:00-05:59", time(0, 0), time(5, 59)),
    ("06:00-11:59", time(6, 0), time(11, 59)),
    ("12:00-17:59", time(12, 0), time(17, 59)),
    ("18:00-23:59", time(18, 0), time(23, 59))
]

# Upload de dados
with st.sidebar:
    uploaded_file = st.file_uploader(label="Fazer Upload dos dados criminais!", help="Clique no botão abaixo 'Browse Files'", type=["csv"])
    if uploaded_file is not None and not st.session_state.dados_carregados:
        try:
            st.session_state.crime_data = CrimeData(uploaded_file)
            previsor = PrevisorCrime(st.session_state.crime_data)
            previsor.treinar_modelo()
            cartao_programa = CartaoPrograma(previsor, st.session_state.crime_data)
            st.session_state.pontos_patrulhamento = cartao_programa.gerar_pontos_patrulhamento()
            st.session_state.excel_path = cartao_programa.gerar_excel("cartao_programa.xlsx")
            st.success("Cartão programa gerado com sucesso!")
            st.session_state.dados_carregados = True

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
    
    # Botão de download fora do bloco condicional anterior
    if st.session_state.dados_carregados and st.session_state.excel_path:
        st.download_button(
            label="Baixar Cartões Programa (Excel)",
            data=open(st.session_state.excel_path, "rb").read(),
            file_name="cartões_programa.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if st.session_state.dados_carregados and len(st.session_state.pontos_patrulhamento) > 0:
    try:
        # Gráficos de análise
        st.write("## Gráficos de Análise:")
        col1, col2, col3 = st.columns(3)
        col1.plotly_chart(create_hourly_crime_graph(st.session_state.crime_data.df), use_container_width=True)
        col2.plotly_chart(create_neighborhood_crime_graph(st.session_state.crime_data.df), use_container_width=True)
        col3.plotly_chart(create_weekday_crime_graph(st.session_state.crime_data.df), use_container_width=True)

        col4, col5, col6 = st.columns(3)
        col4.plotly_chart(create_crime_type_pareto_graph(st.session_state.crime_data.df), use_container_width=True)
        col5.plotly_chart(create_crime_trend_graph(st.session_state.crime_data.df), use_container_width=True)
        col6.plotly_chart(create_shift_crime_graph(st.session_state.crime_data.df), use_container_width=True)

        # Seletores para dia e horário
        st.write("## Mapa de Pontos de Patrulhamento:")
        col1, col2 = st.columns(2)
        with col1:
            dia_selecionado = st.selectbox(
                "Selecione o dia da semana:",
                options=[(i, nome) for i, nome in dias_da_semana.items()],
                format_func=lambda x: x[1]
            )
        with col2:
            faixa_horaria = st.selectbox(
                "Selecione a faixa horária:",
                options=[f[0] for f in faixas_horarias]
            )

        # Encontrar os limites de horário selecionados
        horario_inicio = next(f[1] for f in faixas_horarias if f[0] == faixa_horaria)
        horario_fim = next(f[2] for f in faixas_horarias if f[0] == faixa_horaria)

        # Filtrar pontos por dia e horário
        pontos_filtrados = [
            ponto for ponto in st.session_state.pontos_patrulhamento 
            if ponto["DIA_SEMANA"] == dia_selecionado[0] and
            horario_inicio <= ponto["HORARIO_INICIO"].time() <= horario_fim
        ]

        # Criar mapa
        if pontos_filtrados:
            localizacao_inicial = [pontos_filtrados[0]["LATITUDE"], pontos_filtrados[0]["LONGITUDE"]]
            mapa = folium.Map(location=localizacao_inicial, zoom_start=15, tiles='OpenStreetMap')

            for ponto in pontos_filtrados:
                folium.Marker(
                    location=[ponto["LATITUDE"], ponto["LONGITUDE"]],
                    popup=(f"<b>Dia:</b> {dias_da_semana[ponto['DIA_SEMANA']]}<br>"
                           f"<b>Horário:</b> {ponto['HORARIO_INICIO'].strftime('%H:%M')} - {ponto['HORARIO_TERMINO'].strftime('%H:%M')}<br>"
                           f"<b>Bairro:</b> {ponto['BAIRRO']}<br><b>Objetivo:</b> {ponto['OBJETIVO']}"),
                    icon=folium.Icon(color="blue")
                ).add_to(mapa)

            st_folium(mapa, width='100%', height=700)
        else:
            st.warning("Não há pontos de patrulhamento para o dia e horário selecionados.")

    except Exception as e: st.error(f"Ocorreu um erro ao processar os dados: {e}")