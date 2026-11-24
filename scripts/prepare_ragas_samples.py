
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GOLDEN_FILE = ROOT / "data" / "benchmark_golden.json"
OUTPUT_FILE = ROOT / "data" / "benchmark" / "ragas_samples_3.json"

SELECTED_IDS = {"P01", "P06", "P13"}


def main():
    with GOLDEN_FILE.open(encoding="utf-8") as f:
        golden = json.load(f)

    if not isinstance(golden, list):
        raise ValueError("Expected a list of golden samples.")

    samples = []

    for item in golden:
        if item["id"] not in SELECTED_IDS:
            continue

        samples.append({
            "id": item["id"],
            "user_input": item["user_input"],
            "expected_occupation": item["expected_occupation"],
            "expected_uri": item["expected_uri"],
            "reference": item["reference"],
            "reference_contexts": item["reference_contexts"],
            "retrieved_contexts": [],
            "response": None
        })

    if len(samples) != 3:
        raise ValueError(
            f"Expected 3 samples, found {len(samples)}."
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"Output already exists: {OUTPUT_FILE}"
        )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            samples,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("===== RAGAS SAMPLES =====")

    for sample in samples:
        print(
            sample["id"],
            "-",
            sample["expected_occupation"]
        )

    print("\nTotal :", len(samples))
    print("Saved to :", OUTPUT_FILE)


if __name__ == "__main__":
    main()
