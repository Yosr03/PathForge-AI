
import json
from pathlib import Path

INPUT_FILE = Path("data/benchmark/profile_questions.json")
OUTPUT_FILE = Path("data/benchmark_golden.json")

with INPUT_FILE.open("r", encoding="utf-8") as f:
    profiles = json.load(f)

if not isinstance(profiles, list):
    raise ValueError("Le fichier source doit contenir une liste.")

golden_dataset = []

for profile in profiles[:5]:
    golden_dataset.append({
        "id": profile["id"],
        "user_input": profile["query"],
        "expected_occupation": profile["expected_occupation"],
        "expected_uri": profile["expected_uri"],
        "reference": None,
        "reference_contexts": [],
        "retrieved_contexts": [],
        "response": None,
        "validated_by_human": False
    })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(
        golden_dataset,
        f,
        ensure_ascii=False,
        indent=2
    )

print("Golden Dataset initial créé.")
print(f"Nombre d'exemples : {len(golden_dataset)}")
print(f"Fichier : {OUTPUT_FILE}")
print("Statut : brouillon, références à vérifier.")
