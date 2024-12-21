import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import json
import os

class KDBFaiss:
    def __init__(self, model_name, cache_folder, device):
        self.model_name = model_name
        self.cache_folder = cache_folder
        self.device = device
        self.texts = []

        # Criar modelo de embeddings
        self.embedding_model = SentenceTransformer(
            model_name,
            cache_folder=cache_folder,
            device=device
        )

        # Índices FAISS
        self.index_l2 = None

    def add_embeddings(self, embeddings):
        d = embeddings.shape[1]  # Dimensão dos embeddings
        if self.index_l2 is None:
            self.index_l2 = faiss.IndexFlatL2(d)  # Usando L2 (distância euclidiana) como métrica
        self.index_l2.add(embeddings)

    def add_text(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        self.texts.extend(texts)
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        self.add_embeddings(embeddings)

    # Exportacao dos indices do KDB
    def export_kdb(self, filename):
        faiss.write_index(self.index_l2, f"{filename}_l2.index")
        with open(f"{filename}_texts.json", "w", encoding="utf-8") as f:
            json.dump(self.texts, f, ensure_ascii=False)

    @staticmethod
    def import_kdb(filename):
        kdb = KDBFaiss(model_name=None, cache_folder=None, device=None)
        kdb.index_l2 = faiss.read_index(f"{filename}_l2.index")
        with open(f"{filename}_texts.json", "r", encoding="utf-8") as f:
            kdb.texts = json.load(f)
        return kdb

    # Busca de termos na base vetorial
    def search(self, query, k=5):
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index_l2.search(query_embedding, k)
        results = [self.texts[i] for i in indices[0]]
        return results

if __name__ == "__main__":
    # Configurações
    MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
    CACHE_FOLDER = "./cache"
    DEVICE = "cpu"  # Altere para "cuda" se houver suporte a GPU

    # Carregar dados
    data_dir = "data/"
    proposicoes_file = os.path.join(data_dir, "proposicoes_deputados.parquet")
    despesas_file = os.path.join(data_dir, "serie_despesas_diárias_deputados.parquet")
    deputados_file = os.path.join(data_dir, "deputados.parquet")
    sumarizacao_file = os.path.join(data_dir, "sumarizacao_proposicoes.json")

    # Carregar e combinar dados
    df_proposicoes = pd.read_parquet(proposicoes_file)
    df_despesas = pd.read_parquet(despesas_file)
    df_deputados = pd.read_parquet(deputados_file)

    with open(sumarizacao_file, "r", encoding="utf-8") as f:
        sumarizacao = json.load(f)

    texts = (
        df_proposicoes.to_string(index=False).split("\n") +
        df_despesas.to_string(index=False).split("\n") +
        df_deputados.to_string(index=False).split("\n") +
        [item["assistant"] for item in sumarizacao["Resumo"]]
    )

    # Criar base FAISS
    kdb = KDBFaiss(MODEL_NAME, CACHE_FOLDER, DEVICE)
    kdb.add_text(texts)

    # Exportar a base FAISS
    kdb.export_kdb(os.path.join(data_dir, "faiss_index"))
    print("Base FAISS criada e exportada com sucesso.")
