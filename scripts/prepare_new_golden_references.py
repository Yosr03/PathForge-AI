
import json
from pathlib import Path

GOLDEN_PATH = Path("data/benchmark_golden.json")
ESCO_PATH = Path("data/processed/esco_documents_clean.json")

SKILLS = {
    "P06": [
        "statistics",
        "statistical modeling techniques",
        "data science",
        "report analysis results",
    ],
    "P07": [
        "establish data processes",
        "process data",
        "develop data processing applications",
        "data storage",
    ],
    "P08": [
        "analyse business requirements",
        "interact with users to gather requirements",
        "define technical requirements",
    ],
    "P09": [
        "execute software tests",
        "report test findings",
        "provide software testing documentation",
    ],
    "P10": [
        "manage database",
        "perform backups",
        "maintain database performance",
        "maintain database security",
    ],
    "P11": [
        "web programming",
        "use markup languages",
        "style sheet languages",
        "web services",
    ],
    "P12": [
        "design computer network",
        "ICT network routing",
        "analyse network configuration and performance",
    ],
    "P13": [
        "assessment of risks and threats",
        "implement ICT risk management",
        "risk management",
    ],
    "P14": [
        "robotics",
        "robotic components",
        "automatic control system",
        "design automation components",
    ],
    "P15": [
        "embedded systems",
        "security engineering",
        "identify ICT system weaknesses",
        "perform ICT security testing",
    ],
}

EXPLANATIONS = {
    "P06": (
        "Predictive modelling and statistical methods support "
        "a connection with statistics and statistical modeling "
        "techniques. Data analysis and communication of findings "
        "also support data science and report analysis results."
    ),
    "P07": (
        "ETL pipelines and automated ingestion relate to "
        "establishing data processes. Dataset transformation "
        "supports process data and developing data processing "
        "applications. Data storage is a related occupational "
        "requirement, not explicitly demonstrated."
    ),
    "P08": (
        "Gathering stakeholder needs relates to analysing "
        "business requirements and interacting with users "
        "to gather requirements. Translating those needs "
        "into specifications relates to defining technical "
        "requirements."
    ),
    "P09": (
        "Automated test execution relates to executing software "
        "tests. Defect reporting relates to reporting test "
        "findings. Test cases support testing documentation, "
        "although complete documentation is not explicitly shown."
    ),
    "P10": (
        "Database server administration relates to managing "
        "databases. Backups and recovery relate to performing "
        "backups. Monitoring and access control relate to "
        "maintaining performance and database security."
    ),
    "P11": (
        "Building websites with HTML, CSS and JavaScript relates "
        "to web programming, markup languages and style sheet "
        "languages. Backend API integration relates to web "
        "services."
    ),
    "P12": (
        "Network design relates to designing computer networks. "
        "Router configuration relates to ICT network routing. "
        "Troubleshooting and monitoring relate to analysing "
        "network configuration and performance."
    ),
    "P13": (
        "Assessing vulnerabilities and cybersecurity risks "
        "relates to assessment of risks and threats. Risk "
        "mitigation plans relate to implementing ICT risk "
        "management and broader risk management."
    ),
    "P14": (
        "Robotic system development relates to robotics and "
        "robotic components. Control algorithms and automation "
        "projects relate to automatic control systems and "
        "designing automation components."
    ),
    "P15": (
        "Firmware and microcontroller experience relates to "
        "embedded systems. Hardware vulnerability analysis "
        "relates to security engineering and identifying ICT "
        "system weaknesses. Formal security testing remains "
        "an occupational requirement not explicitly demonstrated."
    ),
}

with GOLDEN_PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

with ESCO_PATH.open("r", encoding="utf-8") as f:
    esco = json.load(f)

esco_by_uri = {item["id"]: item for item in esco}

# Préparer les changements en mémoire uniquement
updated = 0

for example in golden:
    profile_id = example["id"]

    if profile_id not in SKILLS:
        continue

    if example.get("validated_by_human"):
        raise ValueError(
            f"{profile_id} est déjà validé : modification refusée."
        )

    occupation = esco_by_uri.get(example["expected_uri"])

    if occupation is None:
        raise ValueError(
            f"Métier ESCO introuvable pour {profile_id}"
        )

    essential = set(occupation.get("essential_skills", []))
    selected = SKILLS[profile_id]

    missing = [skill for skill in selected if skill not in essential]

    if missing:
        raise ValueError(
            f"{profile_id} : compétences absentes d'ESCO : {missing}"
        )

    skills_text = ", ".join(f"'{skill}'" for skill in selected)

    reference = (
        f"The recommended occupation is {occupation['title']}. "
        f"{EXPLANATIONS[profile_id]} "
        f"The selected ESCO essential skills are: {skills_text}. "
        "This recommendation is based on the stated profile "
        "and ESCO v1.2.1 occupation requirements. "
        "It does not certify the student's competence."
    )

    example["selected_essential_skills"] = selected
    example["reference_final"] = reference
    example["reference_status"] = "pending_human_validation"
    example["validated_by_human"] = False
    example["reference_source"] = "ESCO v1.2.1"
    example["reference_source_uri"] = occupation["id"]

    # Ne pas renseigner reference avant validation humaine
    updated += 1

if updated != 10:
    raise ValueError(
        f"10 profils attendus, {updated} trouvés. "
        "Aucun fichier enregistré."
    )

# Sauvegarde de l'état précédent
backup_path = Path("data/benchmark_golden_before_p06_p15.json")

if not backup_path.exists():
    backup_path.write_text(
        GOLDEN_PATH.read_text(encoding="utf-8"),
        encoding="utf-8"
    )

GOLDEN_PATH.write_text(
    json.dumps(golden, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("Références P06 à P15 préparées avec succès.")
print(f"Profils enrichis : {updated}")
print(f"Sauvegarde : {backup_path}")

for example in golden:
    if example["id"] in SKILLS:
        print(
            f"{example['id']} | "
            f"{example['expected_occupation']} | "
            f"{len(example['selected_essential_skills'])} compétences | "
            f"validation={example['validated_by_human']}"
        )
