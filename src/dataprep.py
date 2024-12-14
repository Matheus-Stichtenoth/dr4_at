import pandas as pd
import os
import json
import requests
import seaborn as sns
import google.generativeai as genai
from services.summarizer import ChunkSummary
from dotenv import load_dotenv

load_dotenv('.env')

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

#############################
#########ATIVIDADE 3#########
#############################

#Lendo os dados do parquet criado para gerar o gráfico
df_deputados = pd.read_parquet('data/deputados.parquet')

def exercicio_3():
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

#############################
#########ATIVIDADE 4#########
#############################

def exercicio_4(): 
    
    ids = df_deputados['id'].unique()

    df_deputados_despesas = pd.DataFrame()

    for id in range(len(ids)):
        print(f'{id} / {len(ids)}')
        print(f'⚜ {ids[id]} - Lendo dados')
        url_deputado = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{ids[id]}/despesas'
        response = requests.get(url_deputado)
        data = response.json()
        data_fixed = data.get("dados", [])
        df_deputado = pd.DataFrame(data_fixed)
        df_deputado['id'] = ids[id]
        df_deputado = df_deputado.merge(df_deputados, how='left', left_on='id', right_on='id')
        df_deputado = df_deputado[['tipoDespesa', 'dataDocumento','valorLiquido','nome','siglaPartido']]
        df_deputado['dataDocumento'] = pd.to_datetime(df_deputado['dataDocumento']).dt.date
        
        df_deputados_despesas = pd.concat([df_deputados_despesas, df_deputado], ignore_index=True)

    df_deputados_despesas.to_parquet('data/serie_despesas_diárias_deputados.parquet')

    df_deputados_despesas = pd.read_parquet('data/serie_despesas_diárias_deputados.parquet')

    summary = df_deputados_despesas.describe(include='all').to_string()

    prompt_analysis = f"""
    Você é um analista de dados sênior que trabalha na câmara dos deputados. Seu foco é em apresentar os dados mais distantes da realidade voltados à despesa dos deputados.
    Abaixo estão os dados relevantes:

    {summary}

    A partir dos dados apresentados, você deverá fazer 3 análises de acordo com o que achar melhor.
    Não quero que me retorne códigos como respostas, mas sim, a sua análise dos dados.
    Retorne como resposta um texto que comente sobre as 3 análises e os resultados obtidos por elas.
    """

    print('▶ Gerando análises solicitadas...')
    # Definir a chave de API do Gemini (use a chave fornecida pela sua conta)
    genai.configure(api_key=os.environ["GEMINI_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_analysis)
    print(response.text)

    output_analysis = response.text

    print('💫 Gerando Insights a partir das análises geradas...')
    prompt_generated_knowledge = f"""
    A partir das análises criadas em {output_analysis}, gere insights sobre elas.
    Esses insights, deverão retornar em um formato que eu possa subir para um JSON. 
    Podem ser todos os insights em um único texto dentro desse JSON, para facilitar.
    """
    genai.configure(api_key=os.environ["GEMINI_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_generated_knowledge)
    print(response.text)


#############################
#########ATIVIDADE 5#########
#############################

def exercicio_5():
    temas = [40,46,62]

    df_proposicoes_all = pd.DataFrame()

    for i in range(len(temas)):
        print(f'🧾 Iniciado tema  n° {temas[i]}')
        url_dados_proposicoes = f'https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataInicio=2024-01-01&codTema={temas[i]}&itens=10&ordem=ASC&ordenarPor=id'
        response = requests.get(url_dados_proposicoes)
        data = response.json()
        data_fixed = data.get("dados", [])
        df_proposicoes = pd.DataFrame(data_fixed)
        df_proposicoes_all = pd.concat([df_proposicoes_all, df_proposicoes],ignore_index=True)
        print('Tema Finalizado!')

    print('')

    ids_proposicoes = df_proposicoes_all['id'].unique()

    proposicoes = []
    df_ementa_proposicoes = pd.DataFrame()

    for i in range(len(ids_proposicoes)):
        print(f'🧩 Iniciando Proposicao n° {ids_proposicoes[i]}')
        url_proposicao = f'https://dadosabertos.camara.leg.br/api/v2/proposicoes/{ids_proposicoes[i]}'
        response = requests.get(url_proposicao)
        data = response.json()
        data_fixed = data.get("dados", [])
        proposicao = pd.DataFrame(data_fixed)
        proposicao = proposicao.drop(columns=['statusProposicao'])
        detalhamento_proposicao = proposicao['ementa'][0]
        print(f'Proposicao: {detalhamento_proposicao}')
        df_ementa_proposicoes = pd.concat([df_ementa_proposicoes,proposicao], ignore_index=True)
        proposicoes.append(detalhamento_proposicao)
        print('Proposicao Finalizada! \n')

    df_ementa_proposicoes.to_parquet('data/proposicoes_deputados.parquet')

    USER_PROMPT = "Summarize all the chunks into a single cohesive summary."

    # Criando uma instância do sumarizador
    summarizer = ChunkSummary(
        model_name='gemini-1.5-flash',
        apikey=os.environ["GEMINI_KEY"],
        text=proposicoes,
        window_size=300,
        overlap_size=50,
        system_prompt='Você é um modelo que irá executar resumos eficientes de textos.'
    )

    # Gerando o resumo
    summary = summarizer.summarize(USER_PROMPT)

    # Exibindo o resumo final
    print(f'Resumo Final: {summary}')

#alo