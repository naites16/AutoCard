import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

class PrevisorCrime:
    """Classe para previsão de crimes."""

    def __init__(self, crime_data):
        self.crime_data = crime_data
        self.modelo = None
        self.label_encoder = crime_data.label_encoder  # Armazenando o label encoder
        self.scaler = None  # Armazenando o scaler

    def treinar_modelo(self):
        """Treina o modelo de previsão."""
        # Separar features e target
        features = self.crime_data.df[["BAIRRO_CODIGO", "DIA_SEMANA", "HORARIO_FATO"]]
        target = self.crime_data.df["DESCR_NATUREZA_PRINCIPAL"]

        # Normalizar as features e manter nomes de colunas
        self.scaler = StandardScaler()
        features = pd.DataFrame(self.scaler.fit_transform(features), columns=["BAIRRO_CODIGO", "DIA_SEMANA", "HORARIO_FATO"])

        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2)

        # Criar e treinar o modelo
        self.modelo = LogisticRegression()
        self.modelo.fit(X_train, y_train)

        # Avaliar o modelo
        y_pred = self.modelo.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Acurácia do modelo: {accuracy}")

    def prever_local_horario(self, bairro, dia_semana, hora):
        """Prever o tipo de crime com maior probabilidade para um local e horário específico."""
        # Convertendo o bairro para o código do label encoding
        bairro_codigo = self.label_encoder.transform([bairro])[0]

        # Organizar os dados de entrada em um DataFrame com as mesmas colunas e normalizá-los
        entrada = pd.DataFrame([[bairro_codigo, dia_semana, hora]], columns=["BAIRRO_CODIGO", "DIA_SEMANA", "HORARIO_FATO"])
        entrada = self.scaler.transform(entrada)  # Normaliza a entrada

        # Prever o tipo de crime com maior probabilidade usando o modelo
        previsao = self.modelo.predict_proba(pd.DataFrame(entrada, columns=["BAIRRO_CODIGO", "DIA_SEMANA", "HORARIO_FATO"]))
        tipo_crime = self.modelo.classes_[previsao.argmax()]
        probabilidade = previsao[0][previsao.argmax()]
        return tipo_crime, probabilidade
