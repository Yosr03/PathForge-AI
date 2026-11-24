
import json
import time
from pathlib import Path

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT / "data" / "benchmark" / "questions.json"
OUTPUT_FILE = ROOT / "data" / "benchmark" / "results_comparison.json"

COLLECTIONS = {
    "512/64": "pathforge_esco",
    "256/32": "pathforge_esco_256",
}

TOP_K = 5
MODEL_NAME = "BAAI/bge-m3"

with QUESTIONS_FILE.open("r", encoding="utf-8") as f:
    questions = json.load(f)

if not questions or any(
    not q.get("expected_uri") for q in questions
):
    raise ValueError("Questions ou URI ESCO manquantes.")

# Détecter le champ de texte des questions
def get_question_text(q):
    for key in ("question", "query", "text"):
        value = q.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"Texte manquant pour {q.get('id')}")

client = QdrantClient(url="http://localhost:6333")

for collection in COLLECTIONS.values():
    if not client.collection_exists(collection):
        raise RuntimeError(f"Collection absente : {collection}")

print("Chargement du modèle BGE-M3...")
model = SentenceTransformer(MODEL_NAME, device="cpu")

texts = [get_question_text(q) for q in questions]

print("Calcul des embeddings des 10 questions...")
vectors = model.encode(
    texts,
    normalize_embeddings=True,
    show_progress_bar=True,
)

report = {}

for config, collection in COLLECTIONS.items():
    print(f"\n===== BENCHMARK {config} =====")

    hits = []
    reciprocal_ranks = []
    latencies = []
    details = []

    for q, vector in zip(questions, vectors):
        start = time.perf_counter()

        # Récupérer davantage de chunks pour dédupliquer
        # les métiers avant de calculer le Top-5.
        results = client.search(
            collection_name=collection,
            query_vector=vector.tolist(),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(
                            value="occupation"
                        ),
                    )
                ]
            ),
            limit=100,
            with_payload=True,
        )

        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)

        unique_uris = []
        seen = set()

        for result in results:
            payload = result.payload or {}
            uri = payload.get("occupation_uri")

            if uri and uri not in seen:
                seen.add(uri)
                unique_uris.append(uri)

            if len(unique_uris) == TOP_K:
                break

        expected = q["expected_uri"]
        rank = (
            unique_uris.index(expected) + 1
            if expected in unique_uris
            else None
        )

        hit = int(rank is not None)
        rr = 1 / rank if rank is not None else 0

        hits.append(hit)
        reciprocal_ranks.append(rr)

        details.append({
            "id": q["id"],
            "expected_uri": expected,
            "rank": rank,
            "hit_at_5": hit,
            "reciprocal_rank": rr,
            "latency_ms": round(latency_ms, 2),
            "top_5_uris": unique_uris,
        })

        print(
            f"{q['id']} | "
            f"Hit@5={hit} | "
            f"Rang={rank} | "
            f"Latence={latency_ms:.1f} ms"
        )

    report[config] = {
        "collection": collection,
        "questions": len(questions),
        "hit_at_5": sum(hits) / len(hits),
        "mrr_at_5": sum(reciprocal_ranks) / len(questions),
        "mean_search_latency_ms": sum(latencies) / len(latencies),
        "details": details,
    }

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n========== COMPARAISON FINALE ==========")

for config, result in report.items():
    print(f"\nConfiguration : {config}")
    print(f"Hit@5 : {result['hit_at_5']:.2%}")
    print(f"MRR@5 : {result['mrr_at_5']:.4f}")
    print(
        "Latence moyenne : "
        f"{result['mean_search_latency_ms']:.2f} ms"
    )

print(f"\nRésultats enregistrés : {OUTPUT_FILE}")
