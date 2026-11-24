
import json
import math
import time
from pathlib import Path

from datasets import Dataset
from langchain_ollama import ChatOllama
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from ragas import evaluate
from ragas.metrics import answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_samples_3_generated.json"
)

OUTPUT_FILE = (
    ROOT / "data" / "benchmark" /
    "ragas_answer_relevancy_p01.json"
)


class LocalBGEEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-m3",
            device="cpu"
        )

    def embed_documents(self, texts):
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return vectors.tolist()

    def embed_query(self, text):
        vector = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return vector.tolist()


def main():
    with INPUT_FILE.open(encoding="utf-8") as f:
        samples = json.load(f)

    sample = next(
        item for item in samples
        if item["id"] == "P01"
    )

    if not sample.get("response"):
        raise ValueError("P01 has no generated response.")

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"Result already exists: {OUTPUT_FILE}"
        )

    dataset = Dataset.from_list([
        {
            "question": sample["user_input"],
            "answer": sample["response"],
            "contexts": sample["retrieved_contexts"]
        }
    ])

    print("===== RAGAS ANSWER RELEVANCY P01 =====")
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

    print("Calcul de Answer Relevancy...")
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
    value = float(scores.iloc[0]["answer_relevancy"])

    if not math.isfinite(value):
        raise ValueError("Invalid Answer Relevancy score.")

    print("\n===== RESULTAT =====")
    print("Answer Relevancy :", value)
    print("Temps evaluation :", round(elapsed, 2), "s")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "profile_id": "P01",
                "metric": "answer_relevancy",
                "judge": "gemma2:2b",
                "embeddings": "BAAI/bge-m3",
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
