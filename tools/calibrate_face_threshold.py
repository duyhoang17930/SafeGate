from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np

import config
from src.face_recognition import InsightFaceRecognizer
from src.registration import collect_image_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print same-person and different-person similarity stats.")
    parser.add_argument("--face-dir", default=str(config.FACE_IMAGE_DIR))
    return parser.parse_args()


def summarize(label: str, values: list[float]) -> None:
    if not values:
        print(f"{label}: no pairs")
        return
    arr = np.asarray(values, dtype=np.float32)
    print(
        f"{label}: count={len(values)} min={arr.min():.3f} "
        f"p25={np.percentile(arr, 25):.3f} median={np.median(arr):.3f} "
        f"p75={np.percentile(arr, 75):.3f} max={arr.max():.3f}"
    )


def main() -> None:
    args = parse_args()
    recognizer = InsightFaceRecognizer(
        config.FACE_MODEL_NAME,
        config.FACE_DETECTION_SIZE,
        config.FACE_DB_PATH,
        config.FACE_SIMILARITY_THRESHOLD,
    )
    embeddings_by_person: dict[str, list[np.ndarray]] = {}
    for person_dir in sorted(p for p in Path(args.face_dir).iterdir() if p.is_dir()):
        embeddings = []
        for image_path in collect_image_paths([person_dir]):
            image_embeddings = recognizer.extract_embeddings_from_image(image_path)
            if len(image_embeddings) == 1:
                embeddings.append(image_embeddings[0])
        if embeddings:
            embeddings_by_person[person_dir.name] = embeddings

    same = []
    different = []
    for embeddings in embeddings_by_person.values():
        for a, b in itertools.combinations(embeddings, 2):
            same.append(float(np.dot(a, b)))

    people = list(embeddings_by_person)
    for person_a, person_b in itertools.combinations(people, 2):
        for emb_a in embeddings_by_person[person_a]:
            for emb_b in embeddings_by_person[person_b]:
                different.append(float(np.dot(emb_a, emb_b)))

    summarize("same-person", same)
    summarize("different-person", different)
    print(f"Current config threshold: {config.FACE_SIMILARITY_THRESHOLD:.3f}")


if __name__ == "__main__":
    main()

