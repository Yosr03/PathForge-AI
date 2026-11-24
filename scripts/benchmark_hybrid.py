
import json
import re
import time
from pathlib import Path

from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder


# ============================================================
# 1. CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

QUESTIONS_FILE = DATA_DIR / "benchmark" / "profile_questions.json"
DOCUMENTS_FILE = DATA_DIR / "processed" / "esco_documents_clean.json"
OUTPUT_FILE = DATA_DIR / "benchmark" / "results_profiles_reranked.json"

COLLECTION = "pathforge_esco_256"

MODEL_NAME = "BAAI/bge-m3"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CANDIDATES = 50
DENSE_CHUNKS = 300
TOP_K = 5

RRF_K = 60
DENSE_WEIGHT = 0.8
BM25_WEIGHT = 0.2

RERANK_TOP_N = 20


# ============================================================
# 2. TOKENISATION BM25
# ============================================================

def tokenize(text):
    return re.findall(
        r"\w+",
        text.casefold(),
        flags=re.UNICODE
    )


# ============================================================
# 3. METRIQUES D'EVALUATION
# ============================================================

def evaluate(ranking, expected_uri):
    first_five = ranking[:TOP_K]

    if expected_uri not in first_five:
        return 0, 0.0, None

    rank = first_five.index(expected_uri) + 1

    return 1, 1.0 / rank, rank


# ============================================================
# 4. RECHERCHE DENSE : BGE-M3 + QDRANT
# ============================================================

def dense_search(client, vector):

    hits = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="type",
                    match=models.MatchValue(
                        value="occupation"
                    )
                )
            ]
        ),
        limit=DENSE_CHUNKS,
        with_payload=True
    )

    uris = []
    seen = set()

    for hit in hits:

        uri = (hit.payload or {}).get(
            "occupation_uri"
        )

        if uri and uri not in seen:

            seen.add(uri)
            uris.append(uri)

        if len(uris) >= CANDIDATES:
            break

    return uris


# ============================================================
# 5. RECHERCHE LEXICALE : BM25
# ============================================================

def bm25_search(bm25, documents, query):

    scores = bm25.get_scores(
        tokenize(query)
    )

    indices = sorted(
        range(len(documents)),
        key=lambda i: (
            -float(scores[i]),
            i
        )
    )

    return [
        documents[i]["id"]
        for i in indices[:CANDIDATES]
        if scores[i] > 0
    ]


# ============================================================
# 6. FUSION HYBRIDE : RRF PONDERE 80/20
# ============================================================

def rrf_fusion(dense_uris, bm25_uris):

    fused = {}

    for ranking, weight in [
        (dense_uris, DENSE_WEIGHT),
        (bm25_uris, BM25_WEIGHT)
    ]:

        for rank, uri in enumerate(
            ranking,
            start=1
        ):

            fused[uri] = (
                fused.get(uri, 0.0)
                + weight / (RRF_K + rank)
            )

    return [
        uri
        for uri, score in sorted(
            fused.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )
    ]


# ============================================================
# 7. RERANKING : CROSS-ENCODER
# ============================================================

def rerank_search(
    reranker,
    query,
    hybrid_uris,
    documents_by_uri
):

    # Selection des 20 premiers metiers hybrides
    candidates = [
        uri
        for uri in hybrid_uris
        if uri in documents_by_uri
    ][:RERANK_TOP_N]

    if not candidates:
        return []

    # Construction des paires (profil, metier ESCO)
    pairs = [
        (
            query,
            documents_by_uri[uri].get(
                "text",
                ""
            )
        )
        for uri in candidates
    ]

    # Calcul des scores Cross-Encoder
    scores = reranker.predict(
        pairs,
        batch_size=8,
        show_progress_bar=False
    )

    # Classement par score decroissant
    ranked = sorted(
        zip(candidates, scores),
        key=lambda item: (
            -float(item[1]),
            item[0]
        )
    )

    return [
        uri
        for uri, score in ranked
    ]


# ============================================================
# 8. BENCHMARK PRINCIPAL
# ============================================================

def main():

    # --------------------------------------------------------
    # Chargement des donnees
    # --------------------------------------------------------

    print("Chargement des profils...")

    with QUESTIONS_FILE.open(
        encoding="utf-8"
    ) as f:
        questions = json.load(f)

    print("Chargement du corpus ESCO...")

    with DOCUMENTS_FILE.open(
        encoding="utf-8"
    ) as f:
        documents = json.load(f)

    documents_by_uri = {
        doc["id"]: doc
        for doc in documents
    }

    # --------------------------------------------------------
    # Initialisation BM25
    # --------------------------------------------------------

    print("Construction BM25...")

    corpus = [
        tokenize(doc.get("text", ""))
        for doc in documents
    ]

    bm25 = BM25Okapi(corpus)

    # --------------------------------------------------------
    # Chargement des modeles
    # --------------------------------------------------------

    print("Chargement BGE-M3...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    print("Chargement Cross-Encoder...")

    reranker = CrossEncoder(
        RERANK_MODEL,
        device="cpu",
        max_length=512
    )

    # --------------------------------------------------------
    # Connexion Qdrant
    # --------------------------------------------------------

    print("Connexion Qdrant...")

    client = QdrantClient(
        url="http://localhost:6333"
    )

    # --------------------------------------------------------
    # Calcul des embeddings une seule fois
    # --------------------------------------------------------

    print("Calcul des embeddings des profils...")

    vectors = model.encode(
        [
            q["query"]
            for q in questions
        ],
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # --------------------------------------------------------
    # Initialisation des methodes
    # --------------------------------------------------------

    methods = [
        "dense",
        "bm25",
        "hybrid",
        "reranked"
    ]

    summary = {
        method: {
            "hits": 0,
            "mrr_sum": 0.0,
            "latencies_ms": []
        }
        for method in methods
    }

    details = []

    print("\n===== BENCHMARK PATHFORGE AI =====")

    # --------------------------------------------------------
    # Evaluation des profils
    # --------------------------------------------------------

    for q, vector in zip(
        questions,
        vectors
    ):

        query = q["query"]
        expected_uri = q["expected_uri"]

        # ----------------------------------------------------
        # A. Dense
        # ----------------------------------------------------

        start = time.perf_counter()

        dense = dense_search(
            client,
            vector.tolist()
        )

        dense_ms = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # B. BM25
        # ----------------------------------------------------

        start = time.perf_counter()

        sparse = bm25_search(
            bm25,
            documents,
            query
        )

        bm25_ms = (
            time.perf_counter() - start
        ) * 1000

        # ----------------------------------------------------
        # C. Hybrid RRF
        # ----------------------------------------------------

        start = time.perf_counter()

        hybrid = rrf_fusion(
            dense,
            sparse
        )

        fusion_ms = (
            time.perf_counter() - start
        ) * 1000

        hybrid_ms = (
            dense_ms
            + bm25_ms
            + fusion_ms
        )

        # ----------------------------------------------------
        # D. Cross-Encoder Reranking
        # ----------------------------------------------------

        start = time.perf_counter()

        reranked = rerank_search(
            reranker,
            query,
            hybrid,
            documents_by_uri
        )

        rerank_ms = (
            time.perf_counter() - start
        ) * 1000

        reranked_ms = (
            hybrid_ms
            + rerank_ms
        )

        # ----------------------------------------------------
        # Classements
        # ----------------------------------------------------

        rankings = {
            "dense": dense,
            "bm25": sparse,
            "hybrid": hybrid,
            "reranked": reranked
        }

        latencies = {
            "dense": dense_ms,
            "bm25": bm25_ms,
            "hybrid": hybrid_ms,
            "reranked": reranked_ms
        }

        row = {
            "id": q["id"],
            "query": query,
            "expected_occupation": q[
                "expected_occupation"
            ],
            "expected_uri": expected_uri,
            "methods": {}
        }

        print(
            f"\n{q['id']} : "
            f"{q['expected_occupation']}"
        )

        # ----------------------------------------------------
        # Evaluation des 4 methodes
        # ----------------------------------------------------

        for method in methods:

            hit, rr, rank = evaluate(
                rankings[method],
                expected_uri
            )

            summary[method]["hits"] += hit

            summary[method]["mrr_sum"] += rr

            summary[method][
                "latencies_ms"
            ].append(
                latencies[method]
            )

            row["methods"][method] = {
                "rank_at_5": rank,
                "hit_at_5": hit,
                "reciprocal_rank_at_5": rr,
                "latency_ms": round(
                    latencies[method],
                    2
                ),
                "top5_uris": rankings[
                    method
                ][:TOP_K]
            }

            print(
                f"  {method:8s} | "
                f"rang={str(rank):4s} | "
                f"Hit@5={hit} | "
                f"latence="
                f"{latencies[method]:.1f} ms"
            )

        row["rerank_only_ms"] = round(
            rerank_ms,
            2
        )

        details.append(row)

    # --------------------------------------------------------
    # 9. RESULTATS GLOBAUX
    # --------------------------------------------------------

    results = {
        "configuration": {
            "collection": COLLECTION,
            "embedding_model": MODEL_NAME,
            "rerank_model": RERANK_MODEL,
            "documents": len(documents),
            "questions": len(questions),
            "candidates": CANDIDATES,
            "dense_chunks": DENSE_CHUNKS,
            "top_k": TOP_K,
            "rrf_k": RRF_K,
            "dense_weight": DENSE_WEIGHT,
            "bm25_weight": BM25_WEIGHT,
            "rerank_top_n": RERANK_TOP_N,
            "rerank_batch_size": 8,
            "device": "cpu",
            "latency_scope": (
                "Retrieval and reranking only; "
                "excludes model loading, "
                "BM25 construction and query embedding"
            )
        },
        "summary": {},
        "details": details
    }

    print("\n===== RESULTATS GLOBAUX =====")

    for method in methods:

        data = summary[method]

        n = len(questions)

        hit_rate = (
            data["hits"] / n
        )

        mrr = (
            data["mrr_sum"] / n
        )

        avg_latency = (
            sum(
                data["latencies_ms"]
            ) / n
        )

        results["summary"][method] = {
            "hit_at_5": round(
                hit_rate,
                4
            ),
            "mrr_at_5": round(
                mrr,
                4
            ),
            "mean_latency_ms": round(
                avg_latency,
                2
            )
        }

        print(
            f"{method.upper():8s} | "
            f"Hit@5={hit_rate:.2%} | "
            f"MRR@5={mrr:.4f} | "
            f"Latence={avg_latency:.2f} ms"
        )

    # --------------------------------------------------------
    # 10. SAUVEGARDE JSON
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\nResultats enregistres : "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
