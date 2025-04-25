import json
import logging
import os
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataStoreBuilderFAISS:
    def __init__(self, json_path: str, faiss_path: str, embedding_model: str):
        self.json_path = json_path
        self.faiss_path = faiss_path
        self.embedding_model = embedding_model

    def build(self):
        documents = self._load_documents()
        chunks = self._split_documents(documents)
        self._save_chunks(chunks)

    def _load_documents(self) -> List[Document]:
        with open(self.json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        documents = []
        for entry in raw_data:
            qa_text = f"Section: {entry['section']}\n\nQuestion: {entry['question']}\n\nAnswer: {entry['answer']}"
            documents.append(
                Document(
                    page_content=qa_text,
                    metadata={"type": "faq", "section": entry["section"]},
                )
            )

            for link in entry.get("links", []):
                full_text = (
                    f"Section: {link['section']}\n"
                    f"Related question: {link.get('related_question', '')}\n"
                    f"External content from: {link['url']}\n\n"
                    f"{link['cleaned_content']}"
                )
                documents.append(
                    Document(
                        page_content=full_text,
                        metadata={
                            "type": "link",
                            "section": link["section"],
                            "url": link["url"],
                        },
                    )
                )

        logger.info(f"Loaded {len(documents)} documents from JSON.")
        return documents

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=350,
            chunk_overlap=100,
            length_function=len,
            add_start_index=True,
        )
        chunks = splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def _save_chunks(self, chunks: List[Document]):
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

        db = FAISS.from_documents(chunks, embedding=embeddings)

        faiss_path = self.faiss_path
        if not os.path.exists(faiss_path):
            os.makedirs(faiss_path)

        db.save_local(faiss_path)

        logger.info(f"{len(chunks)} chunks saved in {self.faiss_path}.")
