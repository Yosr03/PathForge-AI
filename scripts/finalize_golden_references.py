
import json
from pathlib import Path

PATH = Path("data/benchmark_golden.json")

with PATH.open("r", encoding="utf-8") as f:
    golden = json.load(f)

explanations = {
    "P01": (
        "The recommended occupation is data analyst. "
        "The student's SQL experience relates to the ESCO skill "
        "'use databases'. Power BI and dashboard creation relate "
        "to 'business intelligence' and 'data visualisation software'. "
        "The sales analysis internship supports a connection with "
        "'business analytics'."
    ),
    "P02": (
        "The recommended occupation is artificial intelligence engineer. "
        "The student's Python programming relates to the ESCO skill "
        "'Python (computer programming)'. Projects involving machine "
        "learning, PyTorch and TensorFlow are consistent with "
        "'artificial neural networks', 'algorithms' and "
        "'principles of artificial intelligence'."
    ),
    "P03": (
        "The recommended occupation is database designer. "
        "The student's experience designing relational schemas "
        "relates to the ESCO skill 'design database scheme'. "
        "Data modelling and database structure optimisation are "
        "consistent with 'database management systems' and "
        "'create database diagrams', although diagram creation "
        "is not explicitly stated in the profile."
    ),
    "P04": (
        "The recommended occupation is software developer. "
        "Building applications with JavaScript and Python relates "
        "to 'computer programming'. API development relates to "
        "'web services'. Git relates to "
        "'tools for software configuration management'. "
        "Writing tests supports software quality, but does not "
        "by itself prove the ESCO skill 'debug software'."
    ),
    "P05": (
        "The recommended occupation is computer vision engineer. "
        "Image classification and object detection projects "
        "relate to the ESCO skills 'image recognition' and "
        "'develop computer vision system'. CNN projects relate "
        "to 'machine learning', while OpenCV experience relates "
        "to 'digital image processing'."
    )
}

for example in golden:
    profile_id = example["id"]

    if profile_id not in explanations:
        raise ValueError(f"Profil inconnu : {profile_id}")

    example["reference_final"] = (
        explanations[profile_id]
        + " This recommendation is based on the stated profile "
        "and ESCO v1.2.1 occupation requirements; it does not "
        "certify the student's competence."
    )

    example["reference_status"] = "pending_human_validation"
    example["validated_by_human"] = False

with PATH.open("w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False, indent=2)

print("Références finales préparées.")

for example in golden:
    print(
        f"{example['id']} | "
        f"{example['expected_occupation']} | "
        f"{len(example['reference_final'])} caractères"
    )

print("Validation humaine : toujours en attente.")
