import json
import math
import time
from pathlib import Path
from statistics import mean

from datasets import Dataset
from langchain_ollama import ChatOllama

from ragas import evaluate
from ragas.metrics import answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig

from scripts.test_ragas_relevancy_p13 import LocalBGEEmbeddings


ROOT = Path(__file__).resolve().parents[1]

BENCHMARK = ROOT / "data" / "benchmark"

INPUT_FILE = (
    BENCHMARK / "ragas_samples_3_generated_v3.json"
)

OUTPUT_FILE = (
    BENCHMARK / "ragas_answer_relevancy_v3.json"
)


def main():

    assert not OUTPUT_FILE.exists(), "Resultat V3 deja existant"

    with INPUT_FILE.open(encoding="utf-8") as f:
        samples = json.load(f)

    assert len(samples) == 3
    assert all(row.get("response") for row in samples)

    dataset = Dataset.from_list([
        {
            "question": row["user_input"],
            "answer": row["response"],
            "contexts": row["retrieved_contexts"]
        }
        for row in samples
    ])

    print("===== RAGAS ANSWER RELEVANCY V3 =====")

    print("Chargement du juge Gemma...")

    judge = ChatOllama(
        model="gemma2:2b",
        base_url="http://localhost:11434",
        temperature=0,
        num_ctx=4096,
        num_predict=512
    )

    llm = LangchainLLMWrapper(judge)

    print("Chargement des embeddings BGE-M3...")

    embeddings = LangchainEmbeddingsWrapper(
        LocalBGEEmbeddings()
    )

    run_config = RunConfig(
        timeout=600,
        max_retries=0,
        max_workers=1
    )

    print("Evaluation des 3 profils...", flush=True)

    start = time.perf_counter()

    result = evaluate(
        dataset=dataset,
        metrics=[answer_relevancy],
        llm=llm,
        embeddings=embeddings,
        run_config=run_config,
        raise_exceptions=True,
        show_progress=True
    )

    elapsed = time.perf_counter() - start

    scores = result.to_pandas()

    results = []

    print("\n===== COMPARAISON V1 / V3 =====")

    for index, sample in enumerate(samples):

        pid = sample["id"]

        v3 = float(
            scores.iloc[index]["answer_relevancy"]
        )

        if not math.isfinite(v3):
            raise ValueError(f"Invalid score: {pid}")

        baseline_file = (
            BENCHMARK /
            f"ragas_answer_relevancy_{pid.lower()}.json"
        )

        with baseline_file.open(encoding="utf-8") as f:
            v1 = float(json.load(f)["score"])

        delta = v3 - v1

        results.append({
            "profile_id": pid,
            "score_v1": v1,
            "score_v3": v3,
            "delta": delta
        })

        print(
            f"{pid} | V1: {v1:.6f}"
            f" | V3: {v3:.6f}"
            f" | Delta: {delta:+.6f}"
        )

    mean_v1 = mean(r["score_v1"] for r in results)
    mean_v3 = mean(r["score_v3"] for r in results)

    target = 0.80

    output = {
        "project": "PathForge AI",
        "metric": "answer_relevancy",
        "prompt_version": "v3",
        "judge": "gemma2:2b",
        "embeddings": "BAAI/bge-m3",
        "profiles": len(results),
        "results": results,
        "mean_v1": mean_v1,
        "mean_v3": mean_v3,
        "delta": mean_v3 - mean_v1,
        "target": target,
        "target_reached": mean_v3 >= target,
        "evaluation_seconds": round(elapsed, 2)
    }

    with OUTPUT_FILE.open("x", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n===== RESULTATS CONSOLIDES =====")
    print(f"Moyenne V1 : {mean_v1:.6f}")
    print(f"Moyenne V3 : {mean_v3:.6f}")
    print(f"Difference : {mean_v3 - mean_v1:+.6f}")
    print(f"Cible      : {target:.2f}")
    print("Cible atteinte :", mean_v3 >= target)
    print("Temps evaluation :", round(elapsed, 2), "s")
    print("Fichier cree :", OUTPUT_FILE)
    print("EVALUATION RELEVANCY V3 OK")


if __name__ == "__main__":
    main()
