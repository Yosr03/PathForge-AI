
import json
from pathlib import Path

GOLDEN_PATH = Path("data/benchmark_golden.json")
ESCO_PATH = Path("data/processed/esco_documents_clean.json")

with GOLDEN_PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

with ESCO_PATH.open("r", encoding="utf-8") as f:
    esco = json.load(f)

esco_by_title = {
    item["title"].strip().lower(): item
    for item in esco
}

new_profiles = [
    {
        "id": "P06",
        "occupation": "data scientist",
        "query": (
            "I use Python to build predictive models, apply statistical "
            "methods and evaluate machine learning algorithms. "
            "I also analyze datasets and communicate findings. "
            "Which occupation best matches my profile?"
        )
    },
    {
        "id": "P07",
        "occupation": "data engineer",
        "query": (
            "I develop ETL pipelines, transform large datasets and "
            "automate data ingestion using Python and SQL. "
            "I have experience with distributed data processing. "
            "Which career fits my profile?"
        )
    },
    {
        "id": "P08",
        "occupation": "ICT business analyst",
        "query": (
            "I gather business requirements, communicate with "
            "stakeholders and translate business needs into "
            "technical specifications for information systems. "
            "Which occupation suits my experience?"
        )
    },
    {
        "id": "P09",
        "occupation": "software tester",
        "query": (
            "I design test cases, execute automated tests and "
            "report software defects. I use testing frameworks "
            "and verify application quality before releases. "
            "Which occupation matches my skills?"
        )
    },
    {
        "id": "P10",
        "occupation": "database administrator",
        "query": (
            "I manage database servers, monitor database performance, "
            "configure backups and restore data after failures. "
            "I also manage user access and database security. "
            "Which occupation best fits my profile?"
        )
    },
    {
        "id": "P11",
        "occupation": "web developer",
        "query": (
            "I develop responsive websites using HTML, CSS and "
            "JavaScript. I integrate frontend interfaces with "
            "backend APIs and optimize web application performance. "
            "Which occupation suits me?"
        )
    },
    {
        "id": "P12",
        "occupation": "ICT network engineer",
        "query": (
            "I configure routers and switches, design computer "
            "networks and troubleshoot connectivity issues. "
            "I also work with network protocols and infrastructure "
            "monitoring. Which career matches my experience?"
        )
    },
    {
        "id": "P13",
        "occupation": "cybersecurity risk manager",
        "query": (
            "I assess cybersecurity risks, identify vulnerabilities "
            "and develop risk mitigation plans. I also work on "
            "security policies, compliance and risk reporting. "
            "Which occupation best matches my profile?"
        )
    },
    {
        "id": "P14",
        "occupation": "robotics engineer",
        "query": (
            "I design robotic systems, program sensors and actuators "
            "and integrate control algorithms. I have worked on "
            "robot navigation and automation projects. "
            "Which occupation suits my skills?"
        )
    },
    {
        "id": "P15",
        "occupation": "embedded systems security engineer",
        "query": (
            "I develop firmware for embedded devices and analyze "
            "security vulnerabilities in connected hardware. "
            "I work with microcontrollers, secure communication "
            "and embedded system protection. "
            "Which occupation best fits my profile?"
        )
    }
]

existing_ids = {item["id"] for item in golden}
added = 0

for profile in new_profiles:
    if profile["id"] in existing_ids:
        print(f"{profile['id']} existe déjà : ignoré.")
        continue

    occupation = esco_by_title.get(
        profile["occupation"].lower()
    )

    if occupation is None:
        raise ValueError(
            f"Métier ESCO introuvable : {profile['occupation']}"
        )

    golden.append({
        "id": profile["id"],
        "user_input": profile["query"],
        "expected_occupation": occupation["title"],
        "expected_uri": occupation["id"],
        "reference": None,
        "reference_contexts": [occupation["text"]],
        "retrieved_contexts": [],
        "response": None,
        "reference_source": "ESCO v1.2.1",
        "reference_source_uri": occupation["id"],
        "validated_by_human": False,
        "reference_status": "draft"
    })

    added += 1

with GOLDEN_PATH.open("w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False, indent=2)

print(f"Nouveaux profils ajoutés : {added}")
print(f"Total Golden Dataset : {len(golden)}")
print(f"Fichier : {GOLDEN_PATH}")

for example in golden:
    print(
        f"{example['id']} | "
        f"{example['expected_occupation']} | "
        f"validated={example['validated_by_human']}"
    )
