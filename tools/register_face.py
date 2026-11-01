from __future__ import annotations

import argparse

import config
from src.face_recognition import InsightFaceRecognizer
from src.registration import FaceRegistrar


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register a new face without retraining ArcFace.")
    parser.add_argument("name", help="Person name to store in the face database.")
    parser.add_argument("--images", nargs="*", default=[], help="Image files or folders to register.")
    parser.add_argument("--capture", action="store_true", help="Capture samples from camera.")
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    parser.add_argument("--width", type=int, default=config.CAMERA_WIDTH)
    parser.add_argument("--height", type=int, default=config.CAMERA_HEIGHT)
    parser.add_argument("--no-copy", action="store_true", help="Do not copy provided images into face_db.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    recognizer = InsightFaceRecognizer(
        config.FACE_MODEL_NAME,
        config.FACE_DETECTION_SIZE,
        config.FACE_DB_PATH,
        config.FACE_SIMILARITY_THRESHOLD,
    )
    registrar = FaceRegistrar(recognizer, config.FACE_IMAGE_DIR)

    image_paths = list(args.images)
    if args.capture:
        captured = registrar.capture_samples(
            args.name,
            args.camera,
            args.width,
            args.height,
            args.samples,
        )
        image_paths.extend(captured)

    count = registrar.register_from_files(args.name, image_paths, copy_images=not args.no_copy)
    print(f"Registered {args.name} from {count} valid images.")
    print(f"Face database: {config.FACE_DB_PATH}")


if __name__ == "__main__":
    main()

