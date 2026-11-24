
import json
import math
import time
from pathlib import Path

from datasets import Dataset
from langchain_ollama import ChatOllama

from ragas import evaluate
from ragas.metrics import context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.run_config import RunConfig


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_samples_3_generated.json"
)

OUTPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_context_recall_p13.json"
)


def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        samples = json.load(f)

    sample = next(
        item for item in samples
        if item["id"] == "P13"
    )

    assert sample["user_input"]
    assert sample["reference"]
    assert sample["retrieved_contexts"]

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"Le resultat existe deja : {OUTPUT_FILE}"
        )

    dataset = Dataset.from_list([
        {
            "question": sample["user_input"],
            "ground_truth": sample["reference"],
            "contexts": sample["retrieved_contexts"]
        }
    ])

    judge = ChatOllama(
        model="gemma2:2b",
        base_url="http://localhost:11434",
        temperature=0,
        num_ctx=4096,
        num_predict=512
    )

    llm = LangchainLLMWrapper(judge)

    run_config = RunConfig(
        timeout=600,
        max_retries=0,
        max_workers=1
    )

    print("===== RAGAS CONTEXT RECALL P13 =====")
    print("Profil : P13")
    print(
        "Contextes :",
        len(sample["retrieved_contexts"])
    )

    print("Calcul de Context Recall...")
    start = time.perf_counter()

    result = evaluate(
        dataset=dataset,
        metrics=[context_recall],
        llm=llm,
        run_config=run_config,
        raise_exceptions=True,
        show_progress=True
    )

    elapsed = time.perf_counter() - start

    scores = result.to_pandas()
    value = float(scores.iloc[0]["context_recall"])

    if not math.isfinite(value):
        raise ValueError("Score Context Recall invalide.")

    print("\n===== RESULTAT =====")
    print("Context Recall :", value)
    print("Temps :", round(elapsed, 2), "secondes")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "profile_id": "P13",
                "metric": "context_recall",
                "judge": "gemma2:2b",
                "score": value,
                "evaluation_seconds": round(elapsed, 2)
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Resultat sauvegarde :", OUTPUT_FILE)


if __name__ == "__main__":
    main()
