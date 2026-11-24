
import argparse
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "esco_documents_clean.json"

DEFAULT_QUERY = "Python SQL data analysis"

def tokenize(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def main():
    parser = argparse.ArgumentParser(
        description="PathForge AI - Recherche lexicale BM25"
    )
    parser.add_argument("--query", type=str, default=DEFAULT_QUERY)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if not args.query.strip():
        parser.error("La question ne doit pas être vide.")
    if args.top_k < 1:
        parser.error("--top-k doit être supérieur ou égal à 1.")

    print("Chargement des documents ESCO...")

    with DATA_FILE.open("r", encoding="utf-8") as f:
        documents = json.load(f)

    # Construction du corpus à partir des documents nettoyés.
    # On réutilise les champs existants sans modifier les données.
    corpus = []

    for doc in documents:
        corpus.append(
            tokenize(str(doc.get("text") or doc.get("title") or ""))
        )

    print(f"Documents chargés : {len(documents)}")
    print("Construction de l'index BM25...")

    bm25 = BM25Okapi(corpus)

    query_tokens = tokenize(args.query)
    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(documents)),
        key=lambda i: scores[i],
        reverse=True
    )

    print(f"\nQuestion : {args.query}")
    print(f"\n===== TOP {args.top_k} BM25 =====")

    for rank, i in enumerate(ranked_indices[:args.top_k], start=1):
        doc = documents[i]

        print(f"\n--- Résultat {rank} ---")
        print("Métier :", doc.get("title"))
        print("Score BM25 :", round(float(scores[i]), 4))
        print("URI ESCO :", doc.get("id"))
        print("Extrait ESCO :", str(doc.get("text") or "")[:350])

    print("\nRecherche BM25 terminée.")


if __name__ == "__main__":
    main()
