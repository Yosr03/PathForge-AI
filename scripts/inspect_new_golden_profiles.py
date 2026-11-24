
import json
from pathlib import Path

GOLDEN_PATH = Path("data/benchmark_golden.json")
ESCO_PATH = Path("data/processed/esco_documents_clean.json")

with GOLDEN_PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

with ESCO_PATH.open("r", encoding="utf-8") as f:
    esco = json.load(f)

esco_by_uri = {item["id"]: item for item in esco}

for example in golden:
    if example["id"] in {
        "P01", "P02", "P03", "P04", "P05"
    }:
        continue

    occupation = esco_by_uri.get(example["expected_uri"])

    if occupation is None:
        print(f"ERREUR : {example['id']} introuvable.")
        continue

    print("\n" + "=" * 75)
    print(f"PROFIL : {example['id']}")
    print(f"MÉTIER : {occupation['title']}")
    print(f"QUESTION : {example['user_input']}")
    print("\nCOMPÉTENCES ESSENTIELLES ESCO :")

    for skill in occupation.get("essential_skills", []):
        print(f" - {skill}")

    print("\nURI ESCO :", occupation["id"])

print("\nInspection terminée. Aucun fichier modifié.")
