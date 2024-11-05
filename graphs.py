import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Definindo as cores padrão
CORES = {
    'primaria': '#102F5D',    # Azul escuro
    'secundaria': '#32417A',  # Azul médio
    'terciaria': '#E3E5ED',   # Cinza claro
    'texto': '#010101'        # Cinza escuro para texto
}



def create_neighborhood_crime_graph(data):
    # Ordena os dados por quantidade de crimes
    dados_ordenados = data.groupby('BAIRRO')['DESCR_NATUREZA_PRINCIPAL'].count().sort_values(ascending=True).tail(10)
    
    fig_bairro = go.Figure()
    fig_bairro.add_trace(go.Bar(
        x=dados_ordenados.values,
        y=dados_ordenados.index,
        orientation='h',
        marker_color=CORES['secundaria'],
        text=dados_ordenados.values,
        textposition='outside'
    ))
    
    fig_bairro.update_layout(
        title='Top 10 Bairros com Mais Ocorrências',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            showline=True,
            linecolor=CORES['primaria']
        ),
        font=dict(color=CORES['texto']),
        title_font=dict(size=24, color=CORES['primaria'])
    )
    return fig_bairro


def create_crime_type_pareto_graph(data):
    crimes_count = data['DESCR_NATUREZA_PRINCIPAL'].value_counts().head(10)
    cum_percent = crimes_count.cumsum() / crimes_count.sum() * 100
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        name='Quantidade',
        x=crimes_count.index,
        y=crimes_count.values,
        marker_color=CORES['secundaria'],
        text=crimes_count.values,
        textposition='outside'
    ))
    
    fig_pareto.add_trace(go.Scatter(
        name='% Acumulada',
        x=crimes_count.index,
        y=cum_percent,
        yaxis='y2',
        line=dict(color=CORES['primaria']),
        text=[f'{val:.1f}%' for val in cum_percent],
        textposition='top center'
    ))
    
    fig_pareto.update_layout(
        title='Top 10 Tipos de Crimes',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=45,
            showgrid=False,
            showline=True,
            linecolor=CORES['primaria']
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis2=dict(
            title='% Acumulada',
            overlaying='y',
            side='right',
            range=[0, 100],
            tickformat=',.0%',
            showgrid=False
        ),
        font=dict(color=CORES['texto']),
        title_font=dict(size=24, color=CORES['primaria']),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    return fig_pareto

def create_crime_trend_graph(data):
    crimes_por_data = data.groupby('DATA_FATO')['DESCR_NATUREZA_PRINCIPAL'].count().reset_index()
    crimes_por_data['DATA_FATO'] = pd.to_datetime(crimes_por_data['DATA_FATO'])
    
    fig_tendencia = go.Figure()
    fig_tendencia.add_trace(go.Scatter(
        x=crimes_por_data['DATA_FATO'],
        y=crimes_por_data['DESCR_NATUREZA_PRINCIPAL'],
        mode='lines',
        line=dict(color=CORES['secundaria']),
        fill='tozeroy',
        fillcolor=CORES['terciaria']
    ))
    
    fig_tendencia.update_layout(
        title='Tendência Temporal de Crimes',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title='',
            showgrid=False,
            showline=True,
            linecolor=CORES['primaria']
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        font=dict(color=CORES['texto']),
        title_font=dict(size=24, color=CORES['primaria']),
        showlegend=False
    )
    return fig_tendencia

def create_shift_crime_graph(data):
    def classificar_turno(hora):
        if 0 <= hora < 6:
            return 'Madrugada<br>(00h-06h)'
        elif 6 <= hora < 12:
            return 'Manhã<br>(06h-12h)'
        elif 12 <= hora < 18:
            return 'Tarde<br>(12h-18h)'
        else:
            return 'Noite<br>(18h-00h)'
    
    data['TURNO'] = data['HORARIO_FATO'].apply(classificar_turno)
    crimes_por_turno = data['TURNO'].value_counts()
    
    fig_pizza = go.Figure()
    fig_pizza.add_trace(go.Pie(
        labels=crimes_por_turno.index,
        values=crimes_por_turno.values,
        textinfo='percent+label',
        textposition='inside',
        marker=dict(colors=[CORES['secundaria'], CORES['terciaria'], CORES['primaria'], CORES['texto']]),
        hoverinfo='label+percent'
    ))
    
    fig_pizza.update_layout(
        title='Distribuição de Crimes por Turno',
        font=dict(color=CORES['texto']),
        title_font=dict(size=24, color=CORES['primaria'])
    )
    return fig_pizza

def create_hourly_crime_graph(data):
    crimes_por_hora = data['HORARIO_FATO'].value_counts().sort_index()

    fig_horario = go.Figure()
    fig_horario.add_trace(go.Bar(
        x=crimes_por_hora.index,
        y=crimes_por_hora.values,
        marker_color=CORES['primaria'],
        marker_line=dict(color=CORES['secundaria'], width=1),
        text=crimes_por_hora.values, # Rótulos de dados
        textposition='outside'     # Posiciona os rótulos fora das barras
    ))

    fig_horario.update_layout(
        title='Distribuição de Crimes por Hora do Dia',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title='Hora do Dia',
            showgrid=False,
            showline=True,
            linecolor=CORES['primaria'],
            tickmode='linear',
            tick0=0,
            dtick=1,
            #range=[-0.5, 16.5],
            type='category'
        ),
        yaxis=dict(  # Oculta o eixo y
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            showline=False #também remove a linha do eixo
        ),
        font=dict(color=CORES['texto']),
        title_font=dict(size=24, color=CORES['primaria'])

    )

    # Ajusta as margens para acomodar os rótulos externos
    fig_horario.update_layout(margin=dict(t=100, b=40, l=0, r=0))  # Ajuste conforme necessário
    return fig_horario



def create_weekday_crime_graph(data): # Inclua CORES como argumento
    # Mapeia os números para os nomes dos dias da semana
    mapeamento_dias = {
        0: 'Segunda',
        1: 'Terça',
        2: 'Quarta',
        3: 'Quinta',
        4: 'Sexta',
        5: 'Sábado',
        6: 'Domingo'
    }

    data['DIA_SEMANA'] = data['DIA_SEMANA'].map(mapeamento_dias)
    ordem_dias = list(mapeamento_dias.values())

    crimes_por_dia = data['DIA_SEMANA'].value_counts().reindex(ordem_dias, fill_value=0)

    fig_dia_semana = go.Figure()
    fig_dia_semana.add_trace(go.Bar(
        x=crimes_por_dia.index,
        y=crimes_por_dia.values,
        marker_color=CORES['secundaria'], # Use CORES aqui
        text=crimes_por_dia.values,
        textposition='outside'
    ))

    fig_dia_semana.update_layout(
        title='Crimes por Dia da Semana',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title='',
            showgrid=False,
            showline=True,
            linecolor=CORES['primaria'], # Use CORES aqui
            type='category'
        ),
        yaxis=dict(
            title='Número de Crimes',
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        ),
        font=dict(color=CORES['texto']), # Use CORES aqui
        title_font=dict(size=24, color=CORES['primaria']) # Use CORES aqui
    )
    return fig_dia_semana