
import json
import time
from pathlib import Path

from app.services.rag_engine import RAGEngine
from app.services.llm_service import LLMService


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_samples_3.json"
)

OUTPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_samples_3_generated.json"
)


def save_results(samples):
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            samples,
            f,
            ensure_ascii=False,
            indent=2
        )


def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        samples = json.load(f)

    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open(encoding="utf-8") as f:
            results = json.load(f)

        if [x["id"] for x in results] != [
            x["id"] for x in samples
        ]:
            raise ValueError(
                "Existing results do not match input samples."
            )
    else:
        results = samples

    pending = [
        sample for sample in results
        if not sample.get("response")
    ]

    if not pending:
        print("All samples already generated.")
        return

    print("Initialisation du moteur RAG...")
    rag = RAGEngine()

    print("Initialisation de Gemma...")
    llm = LLMService()

    for sample in pending:
        sample_id = sample["id"]
        query = sample["user_input"]

        print(f"\n===== {sample_id} =====")
        print("Question :", query)

        start = time.perf_counter()

        retrieval = rag.search(query)

        print("Top-5 ESCO :")
        for doc in retrieval["results"]:
            print("-", doc["title"])

        generation = llm.generate(
            query,
            retrieval["results"]
        )

        total_ms = (
            time.perf_counter() - start
        ) * 1000

        sample["retrieved_contexts"] = [
            doc["text"][:1200]
            for doc in retrieval["results"]
        ]

        sample["response"] = generation["response"]

        sample["retrieved_sources"] = [
            {
                "uri": doc["uri"],
                "title": doc["title"]
            }
            for doc in retrieval["results"]
        ]

        sample["performance"] = {
            "retrieval_ms": retrieval["timings_ms"]["total"],
            "generation_ms": generation["generation_ms"],
            "total_ms": round(total_ms, 2)
        }

        save_results(results)

        print("\nRéponse :")
        print(sample["response"])

        print("\nTemps total :", round(total_ms / 1000, 2), "s")
        print("Progression sauvegardée.")

    print("\n===== TERMINÉ =====")
    print("Fichier :", OUTPUT_FILE)


if __name__ == "__main__":
    main()
