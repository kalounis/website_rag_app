import os

import requests
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.vectorstores.base import VectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = os.path.dirname(__file__)
FAISS_PATH = os.path.join(BASE_DIR, "../../../faiss")
DATASET_PATH = os.path.join(BASE_DIR, "../../../datasets")

INDEX_FAISS_FILE = os.path.join(FAISS_PATH, "index.faiss")
INDEX_PKL_FILE = os.path.join(FAISS_PATH, "index.pkl")
FAQ_DATASET_FILE = os.path.join(DATASET_PATH, "faq_dataset_clean.json")

HF_REPO_BASE = st.secrets["HF_REPO_BASE"]
HF_FAISS_URL = HF_REPO_BASE + "faiss/"
HF_DATASETS_URL = HF_REPO_BASE + "datasets/"

HF_TOKEN = st.secrets["HF_TOKEN"]
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

PROMPT_TEMPLATE = """
You must answer in English only.

Use only the following context to answer the question:

{context}

---

Answer the question based solely on the context: {question}
"""


class RAGPipelineAPIFAISS:
    def __init__(
        self,
        faiss_path: str = FAISS_PATH,
        mistral_api_key=MISTRAL_API_KEY,
        model: str = "mistral-medium",
    ):
        self.faiss_path = faiss_path
        self.mistral_api_key = mistral_api_key
        self.model = model

        self._ensure_faiss_files()
        self._ensure_dataset_file()

        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        self.db: VectorStore = FAISS.load_local(
            folder_path=self.faiss_path,
            embeddings=self.embedding_function,
            index_name="index",
            allow_dangerous_deserialization=True,
        )

        self.prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE)

    def _download_file(self, url, output_path):
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {url} to {output_path}")

    def _ensure_faiss_files(self):
        if not (os.path.exists(INDEX_FAISS_FILE) and os.path.exists(INDEX_PKL_FILE)):
            print("FAISS files not found locally. Downloading from Hugging Face Hub...")
            self._download_file(HF_FAISS_URL + "index.faiss", INDEX_FAISS_FILE)
            self._download_file(HF_FAISS_URL + "index.pkl", INDEX_PKL_FILE)

    def _ensure_dataset_file(self):
        if not os.path.exists(FAQ_DATASET_FILE):
            print(
                "Dataset file not found locally. Downloading from Hugging Face Hub..."
            )
            self._download_file(
                HF_DATASETS_URL + "faq_dataset_clean.json", FAQ_DATASET_FILE
            )

    def query(self, query_text: str):
        results = self.db.similarity_search_with_relevance_scores(query_text, k=3)

        if not results or results[0][1] < 0.2:
            return "No relevant result found", []

        context = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        prompt = self.prompt_template.format(context=context, question=query_text)

        response = self._call_mistral_api(prompt)

        sources = [
            doc.metadata.get("url") or doc.metadata.get("section") for doc, _ in results
        ]
        return response, sources

    def _call_mistral_api(self, prompt: str) -> str:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.mistral_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 512,
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"API Error: {response.status_code} - {response.text}"
