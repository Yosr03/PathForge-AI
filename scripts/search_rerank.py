
import argparse
import json
import re
import time
from pathlib import Path

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "esco_documents_clean.json"

COLLECTION = "pathforge_esco_256"
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

DENSE_WEIGHT = 0.8
BM25_WEIGHT = 0.2
RRF_K = 60
CANDIDATES = 20
DENSE_CHUNKS = 300
RERANK_TOP_N = 20


def tokenize(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default=(
            "I know Python, SQL and Power BI. "
            "I created dashboards and analyzed sales data. "
            "Which occupation matches my profile?"
        )
    )
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if not args.query.strip():
        parser.error("La requête ne doit pas être vide.")

    if not 1 <= args.top_k <= RERANK_TOP_N:
        parser.error("--top-k doit être entre 1 et 20.")

    print("Chargement du corpus ESCO...")

    with DATA_FILE.open(encoding="utf-8") as f:
        documents = json.load(f)

    by_uri = {doc["id"]: doc for doc in documents}

    print("Construction BM25...")
    bm25 = BM25Okapi([
        tokenize(doc.get("text", ""))
        for doc in documents
    ])

    print("Chargement BGE-M3...")
    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL,
        device="cpu"
    )

    print("Chargement Cross-Encoder...")
    reranker = CrossEncoder(
        RERANK_MODEL,
        device="cpu",
        max_length=512
    )

    client = QdrantClient(url="http://localhost:6333")

    # Recherche BM25
    start = time.perf_counter()

    scores = bm25.get_scores(tokenize(args.query))
    indices = sorted(
        range(len(documents)),
        key=lambda i: (-float(scores[i]), i)
    )

    bm25_uris = [
        documents[i]["id"]
        for i in indices[:CANDIDATES]
        if scores[i] > 0
    ]

    # Recherche dense
    vector = embedding_model.encode(
        args.query,
        normalize_embeddings=True
    ).tolist()

    hits = client.search(
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
        limit=DENSE_CHUNKS,
        with_payload=True
    )

    dense_uris = []
    seen = set()

    for hit in hits:
        uri = (hit.payload or {}).get("occupation_uri")

        if uri and uri not in seen:
            seen.add(uri)
            dense_uris.append(uri)

        if len(dense_uris) >= CANDIDATES:
            break

    # Fusion RRF pondérée
    fused = {}

    for ranking, weight in [
        (dense_uris, DENSE_WEIGHT),
        (bm25_uris, BM25_WEIGHT)
    ]:
        for rank, uri in enumerate(ranking, start=1):
            fused[uri] = (
                fused.get(uri, 0.0)
                + weight / (RRF_K + rank)
            )

    hybrid_ranking = [
        uri for uri, score in sorted(
            fused.items(),
            key=lambda item: (-item[1], item[0])
        )
    ]

    candidates = [
        uri for uri in hybrid_ranking
        if uri in by_uri
    ][:RERANK_TOP_N]

    retrieval_ms = (time.perf_counter() - start) * 1000

    # Reranking
    print(f"Reranking de {len(candidates)} métiers...")

    pairs = [
        (args.query, by_uri[uri].get("text", ""))
        for uri in candidates
    ]

    start = time.perf_counter()

    rerank_scores = reranker.predict(
        pairs,
        batch_size=8,
        show_progress_bar=False
    )

    rerank_ms = (time.perf_counter() - start) * 1000

    ranked = sorted(
        zip(candidates, rerank_scores),
        key=lambda item: -float(item[1])
    )

    print(f"\n===== TOP {args.top_k} RERANKÉ =====")
    print("Question :", args.query)

    for rank, (uri, score) in enumerate(
        ranked[:args.top_k],
        start=1
    ):
        doc = by_uri[uri]

        print(f"\n--- Résultat {rank} ---")
        print("Métier :", doc["title"])
        print("Score Cross-Encoder :", round(float(score), 4))
        print("URI ESCO :", uri)
        print("Extrait :", doc.get("text", "")[:250])

    print(f"\nRecherche initiale : {retrieval_ms:.1f} ms")
    print(f"Reranking : {rerank_ms:.1f} ms")
    print(
        f"Temps total hors chargement : "
        f"{retrieval_ms + rerank_ms:.1f} ms"
    )


if __name__ == "__main__":
    main()
