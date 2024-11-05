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
from utils import dias_da_semana
import pandas as pd

st.set_page_config(
    page_title="Cartão Programa Automatizado",
    layout='wide', page_icon='img/icon.png'
)

st.markdown(
    f"""
    <style>
    {open('style.css').read()}
    </style>
    """,
    unsafe_allow_html=True
)
st.header('Sistema de Geração de Cartão Programa Automatizado')
st.sidebar.image('img/icon.png', caption='Cartão Programa Automatizado')

with st.sidebar:
    uploaded_file = st.file_uploader(label="Fazer Upload dos dados criminais!", help="Clique no botão abaixo 'Browse Files'", type=["csv"])
    if uploaded_file is not None:
        try:
            crime_data = CrimeData(uploaded_file)
            previsor = PrevisorCrime(crime_data)
            previsor.treinar_modelo()
            cartao_programa = CartaoPrograma(previsor, crime_data)
            cartao_programa.gerar_pontos_patrulhamento()
            excel_path = cartao_programa.gerar_excel("cartao_programa.xlsx")
            st.success("Cartão programa gerado com sucesso!")

            st.download_button(
                label="Baixar Cartões Programa (Excel)",
                data=open(excel_path, "rb").read(),
                file_name="cartões_programa.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

st.markdown(
    f"""
    <style>
    {open('style.css').read()}
    </style>
    """,
    unsafe_allow_html=True
)
st.write("## Gráficos de Análise:")

if uploaded_file is not None:
    try:
        relatorio = crime_data.gerar_relatorio()

        # Primeira linha de gráficos
        col1, col2, col3 = st.columns(3)

        with col1:
            fig_horario = create_hourly_crime_graph(relatorio)
            st.plotly_chart(fig_horario, use_container_width=True)

        with col2:
            fig_bairro = create_neighborhood_crime_graph(relatorio)
            st.plotly_chart(fig_bairro, use_container_width=True)

        with col3:
            fig_dia_semana = create_weekday_crime_graph(relatorio)
            st.plotly_chart(fig_dia_semana, use_container_width=True)

        # Segunda linha de gráficos
        col4, col5, col6 = st.columns(3)

        with col4:
            fig_pareto = create_crime_type_pareto_graph(crime_data.df)
            st.plotly_chart(fig_pareto, use_container_width=True)

        with col5:
            fig_tendencia = create_crime_trend_graph(crime_data.df)
            st.plotly_chart(fig_tendencia, use_container_width=True)

        with col6:
            fig_pizza = create_shift_crime_graph(crime_data.df)
            st.plotly_chart(fig_pizza, use_container_width=True)

        st.write("## Mapa de Pontos de Patrulhamento:")

        # Gerar o mapa em uma coluna de largura total
        col_mapa = st.columns(1)[0]
        
        # Gerar o mapa - Centralizado na primeira coordenada
        primeiro_ponto = cartao_programa.pontos_patrulhamento[0] if cartao_programa.pontos_patrulhamento else None
        localizacao_mapa = [primeiro_ponto["LATITUDE"], primeiro_ponto["LONGITUDE"]] if primeiro_ponto else [-16.36506, -46.9020118]
        m = folium.Map(location=localizacao_mapa, zoom_start=15, tiles='OpenStreetMap', control_scale=True)

        cores = ["red", "blue", "green", "purple", "orange", "darkred", "lightgray"]
        for dia in range(7):
            pontos_dia = [ponto for ponto in cartao_programa.pontos_patrulhamento if ponto["DIA_SEMANA"] == dia]
            cor = cores[dia % len(cores)]
            for ponto in pontos_dia:
                try:
                    folium.Marker(
                        location=[ponto["LATITUDE"], ponto["LONGITUDE"]],
                        popup=f"<b>Dia:</b> {dias_da_semana[dia]}<br><b>Horário:</b> {ponto['HORARIO_INICIO'].strftime('%H:%M')} - {ponto['HORARIO_TERMINO'].strftime('%H:%M')}<br><b>Bairro:</b> {ponto['BAIRRO']}<br><b>Objetivo:</b> {ponto['OBJETIVO']}",
                        icon=folium.Icon(color=cor)
                    ).add_to(m)
                except Exception as e:
                    print(f"Erro ao adicionar marcador: {e}")

        with col_mapa:
            st_folium(m, width='100%', returned_objects=[])
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")

     # Tabela de Esquema de Cores
    esquema_cores = pd.DataFrame(list(zip(dias_da_semana.values(), [f"<td style='background-color:{cor}'>{dia}</td>" for cor, dia in zip(cores, dias_da_semana.values())])), columns=["Dia", "Cor"])
    st.write("### Esquema de Cores do mapa")
    st.write(esquema_cores.to_html(index=False, escape=False, header=False), unsafe_allow_html=True)