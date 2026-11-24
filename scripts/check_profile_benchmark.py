
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROFILES_FILE = ROOT / "data" / "benchmark" / "profile_questions.json"
ESCO_FILE = ROOT / "data" / "processed" / "esco_documents_clean.json"


def main():
    with PROFILES_FILE.open(encoding="utf-8") as f:
        profiles = json.load(f)

    with ESCO_FILE.open(encoding="utf-8") as f:
        occupations = json.load(f)

    # Index des métiers ESCO par titre exact
    by_title = {}

    for occupation in occupations:
        title = occupation["title"].strip().casefold()
        by_title.setdefault(title, []).append(occupation)

    errors = 0

    print("\n===== VÉRIFICATION DES PROFILS ESCO =====\n")

    for profile in profiles:
        target = profile["target_occupation"]
        matches = by_title.get(target.strip().casefold(), [])

        print(f"{profile['id']} : {target}")

        if len(matches) == 1:
            occupation = matches[0]

            profile["expected_occupation"] = occupation["title"]
            profile["expected_uri"] = occupation["id"]

            print("Statut : OK")
            print("URI :", occupation["id"])

        else:
            errors += 1
            print("Statut : À VÉRIFIER")
            print("Nombre de correspondances :", len(matches))

        print()

    if errors:
        print(f"{errors} correspondance(s) à vérifier.")
        print("Aucune modification du fichier.")
        return

    with PROFILES_FILE.open("w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

    print(f"Vérification terminée : {len(profiles)}/{len(profiles)}")
    print("URI ESCO ajoutées dans profile_questions.json")


if __name__ == "__main__":
    main()
