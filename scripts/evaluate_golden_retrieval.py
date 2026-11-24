
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from app.services.rag_engine import RAGEngine

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "benchmark_golden.json"
OUTPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "results_golden_retrieval_15.json"
)


def evaluate(ranking, expected_uri):
    top5 = ranking[:5]

    if expected_uri not in top5:
        return 0, 0.0, None

    rank = top5.index(expected_uri) + 1
    return 1, 1.0 / rank, rank


def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        examples = json.load(f)

    if len(examples) != 15:
        raise ValueError("15 profils attendus.")

    if not all(
        example.get("validated_by_human")
        for example in examples
    ):
        raise ValueError("Tous les profils doivent être validés.")

    print("Initialisation du moteur RAG...")
    engine = RAGEngine()

    results = []
    summary = {
        "before": {"hits": 0, "mrr_sum": 0.0},
        "after": {"hits": 0, "mrr_sum": 0.0}
    }

    for example in examples:
        profile_id = example["id"]
        query = example["user_input"]
        expected_uri = example["expected_uri"]

        print(
            f"\nÉvaluation {profile_id} : "
            f"{example['expected_occupation']}",
            flush=True
        )

        start = time.perf_counter()
        result = engine.search(query)
        elapsed = (time.perf_counter() - start) * 1000

        before = [
            item["uri"]
            for item in result["before_reranking"]
        ]

        after = [
            item["uri"]
            for item in result["results"]
        ]

        row = {
            "id": profile_id,
            "expected_occupation": example["expected_occupation"],
            "expected_uri": expected_uri,
            "before_top5": before,
            "after_top5": after,
            "timings_ms": result["timings_ms"],
            "elapsed_ms": round(elapsed, 2)
        }

        for method, ranking in [
            ("before", before),
            ("after", after)
        ]:
            hit, rr, rank = evaluate(
                ranking,
                expected_uri
            )

            summary[method]["hits"] += hit
            summary[method]["mrr_sum"] += rr

            row[method] = {
                "hit_at_5": hit,
                "reciprocal_rank_at_5": rr,
                "rank_at_5": rank
            }

        results.append(row)

        print(
            f"  Avant : rang={row['before']['rank_at_5']} "
            f"| Après : rang={row['after']['rank_at_5']} "
            f"| Temps={elapsed / 1000:.2f}s",
            flush=True
        )

        # Sauvegarde progressive pour ne pas perdre
        # les résultats si l'exécution est interrompue.
        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "completed": len(results),
                    "total": len(examples),
                    "results": results
                },
                f,
                ensure_ascii=False,
                indent=2
            )

    n = len(results)

    metrics = {}

    for method in ("before", "after"):
        metrics[method] = {
            "hit_at_5": round(
                summary[method]["hits"] / n, 4
            ),
            "mrr_at_5": round(
                summary[method]["mrr_sum"] / n, 4
            )
        }

    report = {
        "completed": n,
        "total": len(examples),
        "metrics": metrics,
        "results": results
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n===== RÉSULTATS FINAUX =====")

    for method, data in metrics.items():
        print(
            f"{method.upper()} | "
            f"Hit@5={data['hit_at_5']:.2%} | "
            f"MRR@5={data['mrr_at_5']:.4f}"
        )

    print(f"\nRésultats sauvegardés : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
