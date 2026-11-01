from __future__ import annotations

import argparse
from pathlib import Path

import config
from src.face_recognition import InsightFaceRecognizer
from src.registration import collect_image_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build face embeddings from face_db/<person> images.")
    parser.add_argument("--face-dir", default=str(config.FACE_IMAGE_DIR))
    parser.add_argument("--db", default=str(config.FACE_DB_PATH))
    parser.add_argument("--model", default=config.FACE_MODEL_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    recognizer = InsightFaceRecognizer(
        args.model,
        config.FACE_DETECTION_SIZE,
        args.db,
        config.FACE_SIMILARITY_THRESHOLD,
    )
    face_dir = Path(args.face_dir)
    if not face_dir.exists():
        raise FileNotFoundError(f"Face image directory not found: {face_dir}")

    rebuilt: dict[str, object] = {}
    for person_dir in sorted(p for p in face_dir.iterdir() if p.is_dir()):
        image_paths = collect_image_paths([person_dir])
        if not image_paths:
            print(f"Skipping {person_dir.name}: no images")
            continue
        count = recognizer.add_person_from_images(person_dir.name, image_paths)
        rebuilt[person_dir.name] = recognizer.face_db[person_dir.name]
        print(f"{person_dir.name}: {count} valid images")

    recognizer.save_database(rebuilt)
    print(f"Saved face database: {args.db}")


if __name__ == "__main__":
    main()

