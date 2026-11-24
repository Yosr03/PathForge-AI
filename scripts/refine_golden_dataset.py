
import json
from pathlib import Path

GOLDEN_PATH = Path("data/benchmark_golden.json")
ESCO_PATH = Path("data/processed/esco_documents_clean.json")

with GOLDEN_PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

with ESCO_PATH.open("r", encoding="utf-8") as f:
    esco = json.load(f)

esco_by_uri = {doc["id"]: doc for doc in esco}

# Sélection manuelle de compétences réellement présentes
# dans les listes essentielles ESCO.
selected_skills = {
    "P01": [
        "business intelligence",
        "data visualisation software",
        "use databases",
        "business analytics"
    ],
    "P02": [
        "Python (computer programming)",
        "artificial neural networks",
        "algorithms",
        "principles of artificial intelligence"
    ],
    "P03": [
        "design database scheme",
        "database management systems",
        "create database diagrams"
    ],
    "P04": [
        "computer programming",
        "web services",
        "tools for software configuration management",
        "debug software"
    ],
    "P05": [
        "machine learning",
        "image recognition",
        "digital image processing",
        "develop computer vision system"
    ]
}

for example in golden:
    profile_id = example["id"]
    occupation = esco_by_uri[example["expected_uri"]]

    essential = set(occupation["essential_skills"])
    skills = selected_skills[profile_id]

    missing = [skill for skill in skills if skill not in essential]

    if missing:
        raise ValueError(
            f"{profile_id}: compétences absentes d'ESCO : {missing}"
        )

    title = occupation["title"]

    example["reference_original"] = example["reference"]

    example["reference_short"] = (
        f"The most relevant occupation for this profile is "
        f"{title}. The student's documented experience is "
        f"consistent with this occupation. "
        f"ESCO v1.2.1 identifies the following essential "
        f"skills as particularly relevant: "
        f"{', '.join(skills)}. "
        f"This is a career recommendation, not a certification "
        f"of the student's skills."
    )

    example["selected_essential_skills"] = skills
    example["validated_by_human"] = False

with GOLDEN_PATH.open("w", encoding="utf-8") as f:
    json.dump(golden, f, indent=2, ensure_ascii=False)

print("Références courtes ajoutées avec succès.")

for example in golden:
    print(
        f"{example['id']} | "
        f"{example['expected_occupation']} | "
        f"{len(example['selected_essential_skills'])} compétences"
    )
