
import json
from pathlib import Path
from datetime import date

GOLDEN_PATH = Path("data/benchmark_golden.json")
BACKUP_PATH = Path("data/benchmark_golden_backup.json")

with GOLDEN_PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

expected_ids = {"P01", "P02", "P03", "P04", "P05"}

actual_ids = {item["id"] for item in golden}

if actual_ids != expected_ids or len(golden) != 5:
    raise ValueError(
        "Le Golden Dataset ne contient pas exactement P01 à P05."
    )

# Sauvegarde avant modification
with BACKUP_PATH.open("w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False, indent=2)

for example in golden:
    if not example.get("reference_final"):
        raise ValueError(
            f"Référence finale absente : {example['id']}"
        )

    if not example.get("reference_contexts"):
        raise ValueError(
            f"Contexte ESCO absent : {example['id']}"
        )

    if not example.get("expected_uri"):
        raise ValueError(
            f"URI ESCO absente : {example['id']}"
        )

    # Validation des références après revue et accord utilisateur
    example["validated_by_human"] = True
    example["reference_status"] = "validated"
    example["validation_date"] = date.today().isoformat()
    example["validation_scope"] = (
        "Manual review of occupation relevance, "
        "ESCO essential skills and reference explanation"
    )

    # Traçabilité officielle ESCO
    example["reference_source"] = "ESCO v1.2.1"
    example["reference_source_uri"] = example["expected_uri"]

    # Réponse de référence retenue pour les futures évaluations
    example["reference"] = example["reference_final"]

with GOLDEN_PATH.open("w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False, indent=2)

print("Validation enregistrée avec succès.")
print(f"Exemples validés : {len(golden)}")
print(f"Sauvegarde : {BACKUP_PATH}")
print(f"Fichier final : {GOLDEN_PATH}")

for example in golden:
    print(
        f"{example['id']} | "
        f"{example['expected_occupation']} | "
        f"validated={example['validated_by_human']}"
    )
