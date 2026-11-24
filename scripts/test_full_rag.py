
import json
import time
from pathlib import Path

from app.services.rag_engine import RAGEngine
from app.services.llm_service import LLMService


ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "full_rag_test.json"
)


def main():
    query = (
        "I know Python, SQL and Power BI. "
        "I created dashboards and analyzed sales data. "
        "Which occupation matches my profile?"
    )

    print("Initialisation du moteur Hybrid RAG...")
    rag = RAGEngine()

    print("Initialisation du service Gemma...")
    llm = LLMService()

    print("\nRecherche des métiers ESCO...")
    start = time.perf_counter()

    retrieval = rag.search(query)

    print("\nTop-5 métiers :")
    for index, doc in enumerate(
        retrieval["results"],
        start=1
    ):
        print(f"{index}. {doc['title']}")

    print("\nGénération de la réponse...")
    generation = llm.generate(
        query,
        retrieval["results"]
    )

    total_ms = (
        time.perf_counter() - start
    ) * 1000

    result = {
        "query": query,
        "retrieved_contexts": [
            {
                "uri": doc["uri"],
                "title": doc["title"],
                "text": doc["text"][:1200]
            }
            for doc in retrieval["results"]
        ],
        "response": generation["response"],
        "retrieval_timings_ms": retrieval["timings_ms"],
        "generation_ms": generation["generation_ms"],
        "total_ms": round(total_ms, 2),
        "model": generation["model"]
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n===== RÉPONSE PATHFORGE AI =====")
    print(generation["response"])

    print("\n===== PERFORMANCE =====")
    print(
        "Recherche :",
        retrieval["timings_ms"]["total"],
        "ms"
    )
    print(
        "Génération :",
        generation["generation_ms"],
        "ms"
    )
    print(
        "Total :",
        round(total_ms, 2),
        "ms"
    )

    print("\nRésultat sauvegardé :", OUTPUT_FILE)


if __name__ == "__main__":
    main()
