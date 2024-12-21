import streamlit as st
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
from services.kdb_faiss import KDBFaiss
import os

# Função para carregar o texto do arquivo JSON
def load_summary(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Inicialização do aplicativo Streamlit
st.set_page_config(page_title="Dashboard Deputados", layout="wide")

# Abas do dashboard
tabs = st.tabs(["Overview", "Despesas", "Proposições"])

# Definir o DataFrame principal das despesas
df_deputados = pd.read_parquet('data/serie_despesas_diárias_deputados.parquet')

# Conteúdo da aba Overview
with tabs[0]:
    # Título e Subheader
    st.title("Overview Dados Deputados")
    st.markdown(
        "Essa aplicação tem como objetivo mapear os dados públicos dos deputados, consumindo os dados através da API da Câmara de Deputados, tratando-os através de bibliotecas como pandas, e finalizando a disposição para que estejam prontos para consumo."
    )

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        # Exibir a imagem
        try:
            st.image('data/distribuicao_deputados.png', caption="Distribuição dos Deputados", use_column_width=True)
        except FileNotFoundError:
            st.error("A imagem 'distribuicao_deputados.png' não foi encontrada. Certifique-se de que ela está no caminho correto.")

    with col2:
        # Exibir o JSON ao lado da imagem
        try:
            insights_data = load_summary('data/insights_distribuicao_deputados.json')
            st.subheader("Insights sobre Distribuição")
            st.json(insights_data)  # Exibe os dados JSON no formato legível
        except FileNotFoundError:
            st.error("O arquivo 'insights_distribuicao_deputados.json' não foi encontrado. Certifique-se de que ele está no caminho correto.")
        except json.JSONDecodeError:
            st.error("Erro ao carregar o arquivo JSON. Verifique a formatação do arquivo.")

    # Carregar e exibir o texto do arquivo JSON
    try:
        summary_data = load_summary('data/sumarizacao_proposicoes.json')
        st.subheader("Resumo das Proposições")
        st.json(summary_data)  # Exibe os dados JSON no formato legível
    except FileNotFoundError:
        st.error("O arquivo 'sumarizacao_proposicoes.json' não foi encontrado. Certifique-se de que ele está no caminho correto.")
    except json.JSONDecodeError:
        st.error("Erro ao carregar o arquivo JSON. Verifique a formatação do arquivo.")

def tab_proposicoes():
    st.title("Proposições dos Deputados")

    # Carregar dados
    data_dir = "data/"
    proposicoes_file = os.path.join(data_dir, "proposicoes_deputados.parquet")
    sumarizacao_file = os.path.join(data_dir, "sumarizacao_proposicoes.json")
    faiss_index_file = os.path.join(data_dir, "faiss_index")

    df_proposicoes = pd.read_parquet(proposicoes_file)
    st.subheader("Tabela de Proposições")
    st.dataframe(df_proposicoes)

    # Carregar resumo das proposições
    try:
        resumo_proposicoes = load_summary(sumarizacao_file)
        st.subheader("Resumo das Proposições")
        st.json(resumo_proposicoes)
    except FileNotFoundError:
        st.error("O arquivo 'sumarizacao_proposicoes.json' não foi encontrado. Certifique-se de que ele está no caminho correto.")

    # Adicionar funcionalidade de chat com FAISS
    st.subheader("Assistente Virtual")

    # Carregar base FAISS
    try:
        kdb = KDBFaiss.import_kdb(faiss_index_file)
        st.success("Base FAISS carregada com sucesso.")
    except FileNotFoundError:
        st.error("O arquivo da base FAISS não foi encontrado. Certifique-se de que ela foi criada corretamente.")
        return

    # Interface de chat
    user_query = st.chat_input("Faça uma pergunta sobre as proposições:")
    if user_query:
        st.chat_message("user").markdown(user_query)

        try:
            # Buscar na base FAISS
            results = kdb.search(user_query, k=5)
            context = "\n".join(results)

            # Gerar resposta (simulação, ajuste para integrar com modelo LLM)
            response = f"Baseado nas informações relevantes encontradas: {context}"
            st.chat_message("assistant").markdown(response)
        except AttributeError as e:
            st.error(f"Erro ao processar a consulta: {e}")

# Conteúdo da aba Despesas
with tabs[1]:
    # Título e Subheader
    st.title("Despesas dos Deputados")

    # Carregar insights sobre despesas
    try:
        insights_despesas = load_summary('data/insights_despesas_deputados.json')
        st.subheader("Insights sobre Despesas")
        st.json(insights_despesas)
    except FileNotFoundError:
        st.error("O arquivo 'insights_despesas_deputados.json' não foi encontrado. Certifique-se de que ele está no caminho correto.")
    except json.JSONDecodeError:
        st.error("Erro ao carregar o arquivo JSON. Verifique a formatação do arquivo.")

    # Seleção do deputado
    deputado_selecionado = st.selectbox(
        "Selecione um deputado:", df_deputados['nome'].unique()
    )

    # Filtrar dados do deputado selecionado
    df_despesas_filtrado = df_deputados[df_deputados['nome'] == deputado_selecionado]

    # Gráfico de barras com série temporal usando Seaborn
    if not df_despesas_filtrado.empty:
        st.subheader(f"Série Temporal de Despesas - {deputado_selecionado}")
        plt.figure(figsize=(12, 6))
        sns.barplot(
            x=pd.to_datetime(df_despesas_filtrado['dataDocumento']), 
            y=df_despesas_filtrado['valorLiquido'],
            ci=None
        )
        plt.xlabel("Data")
        plt.ylabel("Valor Líquido (R$)")
        plt.title(f"Despesas de {deputado_selecionado}")
        plt.xticks(rotation=45)
        st.pyplot(plt)
    else:
        st.warning("Nenhuma despesa encontrada para o deputado selecionado.")

# Conteúdo da aba Proposições
with tabs[2]:
    tab_proposicoes()