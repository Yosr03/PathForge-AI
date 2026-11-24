
import argparse
import json
import re
from pathlib import Path

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "esco_documents_clean.json"

COLLECTION = "pathforge_esco_256"
MODEL_NAME = "BAAI/bge-m3"
RRF_K = 60
CANDIDATES = 50


def tokenize(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="Python SQL data analysis"
    )
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if not args.query.strip():
        parser.error("La question ne doit pas être vide.")
    if args.top_k < 1:
        parser.error("--top-k doit être supérieur ou égal à 1.")

    print("Chargement ESCO...")
    with DATA_FILE.open(encoding="utf-8") as f:
        documents = json.load(f)

    by_uri = {doc["id"]: doc for doc in documents}

    # 1. Recherche BM25
    print("Recherche BM25...")
    corpus = [
        tokenize(doc.get("text", ""))
        for doc in documents
    ]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(tokenize(args.query))

    bm25_order = sorted(
        range(len(documents)),
        key=lambda i: (-float(scores[i]), i)
    )

    bm25_uris = [
        documents[i]["id"]
        for i in bm25_order[:CANDIDATES]
        if scores[i] > 0
    ]

    # 2. Recherche dense
    print("Chargement BGE-M3...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    vector = model.encode(
        args.query,
        normalize_embeddings=True
    ).tolist()

    client = QdrantClient(url="http://localhost:6333")

    print("Recherche Qdrant...")
    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="type",
                    match=models.MatchValue(value="occupation")
                )
            ]
        ),
        limit=300,
        with_payload=True
    )

    dense_uris = []
    seen = set()

    for result in results:
        uri = (result.payload or {}).get("occupation_uri")

        if uri and uri not in seen:
            seen.add(uri)
            dense_uris.append(uri)

        if len(dense_uris) >= CANDIDATES:
            break

    # 3. Fusion RRF par URI métier
    fused = {}

    for ranking in (bm25_uris, dense_uris):
        for rank, uri in enumerate(ranking, start=1):
            fused[uri] = (
                fused.get(uri, 0.0)
                + 1.0 / (RRF_K + rank)
            )

    final = sorted(
        fused.items(),
        key=lambda item: (-item[1], item[0])
    )[:args.top_k]

    print(f"\n===== TOP {args.top_k} HYBRID RRF =====")
    print("Question :", args.query)

    for rank, (uri, score) in enumerate(final, start=1):
        doc = by_uri.get(uri, {})

        print(f"\n--- Résultat {rank} ---")
        print("Métier :", doc.get("title", "Inconnu"))
        print("Score RRF :", round(score, 6))
        print("URI ESCO :", uri)
        print("Extrait :", doc.get("text", "")[:250])

    print("\nRecherche hybride terminée.")


if __name__ == "__main__":
    main()
