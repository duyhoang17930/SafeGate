from __future__ import annotations

import argparse
from pathlib import Path

import cv2

import config
from src.face_recognition import InsightFaceRecognizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recognize the largest face in an image.")
    parser.add_argument("image")
    parser.add_argument("--db", default=str(config.FACE_DB_PATH))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    recognizer = InsightFaceRecognizer(
        config.FACE_MODEL_NAME,
        config.FACE_DETECTION_SIZE,
        args.db,
        config.FACE_SIMILARITY_THRESHOLD,
    )
    match = recognizer.recognize_largest_face(image)
    print(f"Predicted: {match.name}")
    print(f"Similarity: {match.similarity:.3f}")


if __name__ == "__main__":
    main()

