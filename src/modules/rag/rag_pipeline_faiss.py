import os

import requests
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.vectorstores.base import VectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

FAISS_PATH = os.path.join(os.path.dirname(__file__), "../../../faiss")
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

PROMPT_TEMPLATE = """
You must answer in English only.

Use only the following context to answer the question:

{context}

---

Answer the question based solely on the context : {question}
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
