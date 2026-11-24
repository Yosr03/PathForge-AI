
import json
from pathlib import Path

GOLDEN_FILE = Path("data/benchmark_golden.json")
ESCO_FILE = Path("data/processed/esco_documents_clean.json")


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


golden = load_json(GOLDEN_FILE)
esco_documents = load_json(ESCO_FILE)

# Indexation en mémoire par URI ESCO
esco_by_uri = {
    document["id"]: document
    for document in esco_documents
}

enriched = 0
missing = []

for example in golden:
    uri = example["expected_uri"]
    occupation = esco_by_uri.get(uri)

    if occupation is None:
        missing.append({
            "id": example["id"],
            "expected_uri": uri
        })
        continue

    title = occupation["title"]
    essential = occupation.get("essential_skills", [])
    optional = occupation.get("optional_skills", [])

    # Contexte de référence directement issu d'ESCO
    reference_context = occupation["text"]

    # Réponse de référence factuelle, sans inventer de compétences
    reference = (
        f"The expected occupation is {title}. "
        f"According to ESCO v1.2.1, its essential skills include: "
        f"{', '.join(essential) if essential else 'none listed'}. "
        f"Its optional skills include: "
        f"{', '.join(optional) if optional else 'none listed'}."
    )

    example["reference"] = reference
    example["reference_contexts"] = [reference_context]
    example["source"] = occupation.get("source", "ESCO v1.2.1")
    example["source_uri"] = uri

    # Les contextes récupérés par le système et les réponses
    # générées seront ajoutés lors de l'évaluation RAG.
    example.setdefault("retrieved_contexts", [])
    example.setdefault("response", None)

    # La validation humaine doit être effectuée séparément.
    example["validated_by_human"] = False

    enriched += 1

if missing:
    print("Métiers introuvables dans ESCO :")
    for item in missing:
        print(item)

    raise SystemExit(
        "Enrichissement interrompu : certaines URI sont introuvables."
    )

# Sauvegarde uniquement après vérification de toutes les URI
with GOLDEN_FILE.open("w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False, indent=2)

print("Enrichissement terminé.")
print(f"Exemples enrichis : {enriched}/{len(golden)}")
print(f"Fichier : {GOLDEN_FILE}")
print("Statut : références ESCO ajoutées, validation humaine requise.")

for example in golden:
    print(
        f"{example['id']} | "
        f"{example['expected_occupation']} | "
        f"{len(example['reference_contexts'])} contexte ESCO"
    )
