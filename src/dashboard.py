import streamlit as st
import json

# Função para carregar o texto do arquivo JSON
def load_summary(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Inicialização do aplicativo Streamlit
st.set_page_config(page_title="Dashboard Deputados", layout="wide")

# Abas do dashboard
tabs = st.tabs(["Overview", "Despesas", "Proposições"])

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