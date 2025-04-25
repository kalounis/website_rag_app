import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../modules")))
import json

from web import WebCrawler


def extract_faq():
    crawler = WebCrawler()
    data = crawler.extract_faq_data()

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../datasets/faq_dataset_clean.json")
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")


if __name__ == "__main__":
    extract_faq()
