import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))
from data import DataStoreBuilderFAISS

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "../../datasets/faq_dataset_clean.json")

    faiss_path = os.path.join(base_dir, "../../faiss")

    builder = DataStoreBuilderFAISS(
        json_path=data_path,
        faiss_path=faiss_path,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
    )
    builder.build()
