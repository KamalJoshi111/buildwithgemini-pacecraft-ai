# Copyright 2026 Google LLC
# Seed script for Firestore training_routines collection

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-3e15bc834bf2"
COLLECTION_NAME = "training_routines"

SEED_ROUTINES = [
    {
        "routine_id": "5k-beginner",
        "title": "5K Couch to Finish Line",
        "target_distance": "5k",
        "difficulty": "Beginner",
        "weekly_mileage": 12,
        "key_workouts": [
            "Walk/Run Intervals (2 mi)",
            "Easy Jog (3 mi)",
            "Long Slow Distance (4 mi)"
        ],
        "description": "A gentle 8-week plan to build stamina and finish your first 5K race comfortably."
    },
    {
        "routine_id": "10k-intermediate",
        "title": "10K Tempo & Speed Builder",
        "target_distance": "10k",
        "difficulty": "Intermediate",
        "weekly_mileage": 25,
        "key_workouts": [
            "Zone 2 Base Run (5 mi)",
            "400m Track Intervals (8 reps)",
            "Tempo Run (6 mi)"
        ],
        "description": "Designed for runners aiming to improve threshold pace and break 50 minutes in the 10K."
    },
    {
        "routine_id": "half-marathon-intermediate",
        "title": "Half Marathon PaceCraft Program",
        "target_distance": "Half Marathon",
        "difficulty": "Intermediate",
        "weekly_mileage": 35,
        "key_workouts": [
            "Zone 2 Easy Run (6 mi)",
            "Half Marathon Pace Intervals (3x2 mi)",
            "Long Progressing Run (12 mi)"
        ],
        "description": "Balanced endurance and stamina training program to target a Half Marathon personal best."
    },
    {
        "routine_id": "marathon-advanced",
        "title": "Marathon Sub-3:15 Peak Endurance Plan",
        "target_distance": "Marathon",
        "difficulty": "Advanced",
        "weekly_mileage": 55,
        "key_workouts": [
            "Marathon Pace Long Run (18 mi)",
            "Yasso 800s Speed Intervals (10 reps)",
            "Recovery Easy Run (7 mi)"
        ],
        "description": "High-volume peak training plan for experienced marathon runners targeting sub-3:15."
    }
]


def seed_firestore():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_ROUTINES:
        doc_ref = collection_ref.document(item["routine_id"])
        doc_ref.set(item)
        print(f"Seeded document: {item['routine_id']} -> {item['title']}")

    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed_firestore()
