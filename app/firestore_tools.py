# Copyright 2026 Google LLC
# Firestore database interface and tools for PaceCraft AI

from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-3e15bc834bf2"
COLLECTION_NAME = "training_routines"

_db_client: Optional[firestore.Client] = None


def _get_db() -> firestore.Client:
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def get_training_routines(
    target_distance: Optional[str] = None,
    difficulty: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves available running training routines from the Firestore backend.

    Args:
        target_distance: Optional filter by target race distance (e.g. '5k', '10k', 'Half Marathon', 'Marathon').
        difficulty: Optional filter by runner difficulty level (e.g. 'Beginner', 'Intermediate', 'Advanced').

    Returns:
        A list of matching training routine dictionaries with their workouts and mileage.
    """
    db = _get_db()
    query = db.collection(COLLECTION_NAME)

    docs = query.stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue

        if target_distance and target_distance.strip():
            doc_dist = str(data.get("target_distance", "")).lower()
            if target_distance.strip().lower() not in doc_dist:
                continue

        if difficulty and difficulty.strip():
            doc_diff = str(data.get("difficulty", "")).lower()
            if difficulty.strip().lower() not in doc_diff:
                continue

        results.append(data)

    return results


def save_training_routine(
    routine_id: str,
    title: str,
    target_distance: str,
    difficulty: str,
    weekly_mileage: int,
    key_workouts: List[str],
    description: str
) -> str:
    """Saves or updates a running training routine in the Firestore backend.

    Args:
        routine_id: Unique string identifier for the routine (e.g., '5k-speed-builder').
        title: Descriptive title for the training routine.
        target_distance: Target race distance (e.g., '5k', '10k', 'Half Marathon', 'Marathon').
        difficulty: Skill/experience level ('Beginner', 'Intermediate', 'Advanced').
        weekly_mileage: Total planned weekly mileage for this program.
        key_workouts: List of key weekly workout descriptions.
        description: Full overview and coaching instructions for the routine.

    Returns:
        Status message indicating successful saving to Firestore.
    """
    db = _get_db()
    routine_data = {
        "routine_id": routine_id,
        "title": title,
        "target_distance": target_distance,
        "difficulty": difficulty,
        "weekly_mileage": weekly_mileage,
        "key_workouts": key_workouts,
        "description": description,
    }

    doc_ref = db.collection(COLLECTION_NAME).document(routine_id)
    doc_ref.set(routine_data)
    return f"Successfully saved training routine '{title}' (ID: {routine_id}) to Firestore!"
