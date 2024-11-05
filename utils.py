dias_da_semana = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}

def interpretar_previsoes(previsao, probabilidade, dia_semana, hora):
    """Interpreta a previsão, gerando uma descrição textual."""
    return f"Alta probabilidade de {previsao} na região no {dias_da_semana[dia_semana]} às {hora}:00. Probabilidade: {probabilidade:.2f}"