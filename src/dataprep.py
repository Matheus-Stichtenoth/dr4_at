import pandas as pd
import os
import json
import requests

url_api = "https://dadosabertos.camara.leg.br/api/v2/deputados"

def api_to_parquet(url, name_doc: str, path: str):
    """
    Gera uma arquivo parquet a partir da conexão com uma API

    url = url da api
    name_doc = nome do documento que será salvo
    path = caminho onde o documento deve ser salvo
    """
    response = requests.get(url)
        
    data = response.json()
        
    data_fixed = data.get("dados", [])
        
    # Convertendo para um DataFrame do pandas
    df = pd.DataFrame(data_fixed)

    df.to_parquet(f'{path}/{name_doc}.parquet')

api_to_parquet(url_api,'deputados','data')

import seaborn as sns
import matplotlib.pyplot as plt

#Lendo os dados do parquet criado para gerar o gráfico
df_deputados = pd.read_parquet('data/deputados.parquet')

# Contar o número de deputados por partido
partido_counts = df_deputados['siglaPartido'].value_counts()

# Criar o gráfico de pizza
plt.figure(figsize=(10, 8))
plt.pie(
    partido_counts,
    labels=partido_counts.index,
    autopct='%1.1f%%',
    startangle=140,
    wedgeprops={'edgecolor': 'black'}
)

# Adicionar título
plt.title('Distribuição de Deputados por Partido', fontsize=14)

# Salvar o gráfico como imagem
output_path = 'data/distribuicao_deputados.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

output_path
