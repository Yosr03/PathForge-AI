
import json
import shutil
from pathlib import Path
from datetime import date

GOLDEN_PATH = Path("data/benchmark_golden.json")
BACKUP_PATH = Path("data/benchmark_golden_before_validation_15.json")

TARGET_IDS = {f"P{i:02d}" for i in range(6, 16)}

with GOLDEN_PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

# Vérifier que les 15 profils sont présents
ids = [item["id"] for item in golden]

if len(ids) != 15 or set(ids) != {
    f"P{i:02d}" for i in range(1, 16)
}:
    raise ValueError("Le Golden Dataset doit contenir P01 à P15.")

# Vérifier les références avant toute modification
for example in golden:
    if example["id"] not in TARGET_IDS:
        continue

    if not example.get("reference_final"):
        raise ValueError(
            f"Référence finale absente : {example['id']}"
        )

    if not example.get("reference_contexts"):
        raise ValueError(
            f"Contexte ESCO absent : {example['id']}"
        )

    if not example.get("selected_essential_skills"):
        raise ValueError(
            f"Compétences ESCO absentes : {example['id']}"
        )

# Sauvegarde de sécurité
if not BACKUP_PATH.exists():
    shutil.copy2(GOLDEN_PATH, BACKUP_PATH)

# Valider uniquement P06 à P15
for example in golden:
    if example["id"] not in TARGET_IDS:
        continue

    example["reference"] = example["reference_final"]
    example["validated_by_human"] = True
    example["reference_status"] = "validated"
    example["validation_date"] = date.today().isoformat()
    example["validation_scope"] = (
        "Reviewed reference explanation and ESCO skill alignment"
    )

with GOLDEN_PATH.open("w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False, indent=2)

print("\nGOLDEN DATASET — PATHFORGE AI")
print("=" * 55)

for example in golden:
    print(
        f"{example['id']} | "
        f"{example['expected_occupation']} | "
        f"validated={example['validated_by_human']}"
    )

validated = sum(
    example.get("validated_by_human", False)
    for example in golden
)

print("=" * 55)
print(f"Total : {len(golden)}")
print(f"Validés : {validated}")
print(f"Sauvegarde : {BACKUP_PATH}")
