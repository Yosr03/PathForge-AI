
import json
from pathlib import Path

from datasets import Dataset
from langchain_ollama import ChatOllama

from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import faithfulness
from ragas.llms import LangchainLLMWrapper


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_samples_3_generated.json"
)

OUTPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_faithfulness_p13.json"
)


def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        samples = json.load(f)

    sample = next(
        item for item in samples
        if item["id"] == "P13"
    )

    if not sample.get("response"):
        raise ValueError("P13 has no generated response.")

    if not sample.get("retrieved_contexts"):
        raise ValueError("P13 has no retrieved contexts.")

    print("===== EVALUATION RAGAS P13 =====")
    print("Profil :", sample["id"])
    print("Metier attendu :", sample["expected_occupation"])
    print("Contextes :", len(sample["retrieved_contexts"]))

    dataset = Dataset.from_list([
        {
            "question": sample["user_input"],
            "answer": sample["response"],
            "contexts": sample["retrieved_contexts"]
        }
    ])

    print("\nConnexion au juge local Gemma...")

    judge = ChatOllama(
        model="gemma2:2b",
        base_url="http://localhost:11434",
        temperature=0,
        num_ctx=4096,
        num_predict=512
    )

    llm = LangchainLLMWrapper(judge)

    print("Calcul de Faithfulness...")
    print("Ce test peut prendre plusieurs minutes.")

    run_config = RunConfig(
        timeout=600,
        max_retries=0,
        max_workers=1
    )

    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness],
        run_config=run_config,
        llm=llm,
        raise_exceptions=True,
        show_progress=True
    )

    scores = result.to_pandas()

    print("\n===== RESULTAT =====")
    print(scores[["faithfulness"]].to_string(index=False))

    value = scores.iloc[0]["faithfulness"]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "profile_id": "P13",
                "metric": "faithfulness",
                "judge": "gemma2:2b",
                "score": (
                    None if value != value
                    else float(value)
                )
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\nResultat sauvegarde :", OUTPUT_FILE)


if __name__ == "__main__":
    main()
