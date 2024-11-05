import pandas as pd
from sklearn.preprocessing import LabelEncoder

class CrimeData:
    """Classe para armazenar e processar dados de crimes."""

    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file, sep=";", encoding="utf-8")  # Especificando o separador ';'
        self.processar_dados()

    def processar_dados(self):
        """Valida e processa os dados de crimes."""
        # Convertendo colunas para os tipos corretos
        self.df["DATA_FATO"] = pd.to_datetime(self.df["DATA_FATO"], format="%d/%m/%Y")
        self.df["HORARIO_FATO"] = pd.to_datetime(self.df["HORARIO_FATO"], format="%H:%M:%S").dt.hour
        self.df["DIA_DA_SEMANA_NUMERICO"] = self.df["DIA_DA_SEMANA_FATO"].map(
            {"SEGUNDA-FEIRA": 0, "TERÇA-FEIRA": 1, "QUARTA-FEIRA": 2, "QUINTA-FEIRA": 3,
             "SEXTA-FEIRA": 4, "SÁBADO": 5, "DOMINGO": 6}
        )

        # Renomeando colunas para melhor legibilidade
        self.df.rename(columns={"DIA_DA_SEMANA_NUMERICO": "DIA_SEMANA"}, inplace=True)

        # Validação básica (adicionar mais validações conforme necessário)
        #self.df = self.df[self.df["LATITUDE"] != -16.36506]  # Excluir dados inválidos (latitude -16.36506)

        # Salvando o mapeamento de bairros para o label encoding
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.df["BAIRRO"])
        self.df["BAIRRO_CODIGO"] = self.label_encoder.transform(self.df["BAIRRO"])

        # Convertendo as coordenadas para números do tipo float, tratando a vírgula como separador decimal
        self.df['LATITUDE'] = self.df['LATITUDE'].astype(str).str.replace(',', '.', regex=False).astype(float, errors='ignore')
        self.df['LONGITUDE'] = self.df['LONGITUDE'].astype(str).str.replace(',', '.', regex=False).astype(float, errors='ignore')


    def gerar_relatorio(self):
        """Gera relatório com estatísticas dos crimes."""
        # Criar relatório com estatísticas (e.g., crimes por bairro, dia da semana, hora)
        # Retornar o relatório para ser exibido na interface do usuário
        return self.df.groupby(["BAIRRO", "DIA_SEMANA", "HORARIO_FATO"])["DESCR_NATUREZA_PRINCIPAL"].count().reset_index()