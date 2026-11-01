import argparse
import time

import numpy as np

from camera import Camera
from config import PREVIEW_ENABLED, REGISTER_SAMPLES, SAMPLE_INTERVAL_SECONDS
from database import add_user, init_database, user_exists
from display import Display
from face_engine import FaceEngine
from preview_server import PreviewServer


def parse_args():
    parser = argparse.ArgumentParser(description="Register a face user from the Raspberry Pi camera.")
    parser.add_argument("--student-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--samples", type=int, default=REGISTER_SAMPLES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_database()
    if user_exists(args.student_id):
        raise SystemExit(f"Student ID already exists: {args.student_id}")

    camera = Camera()
    face_engine = FaceEngine()
    display = Display()
    preview = None
    embeddings = []
    attempts = 0
    max_attempts = args.samples * 8

    try:
        if PREVIEW_ENABLED:
            preview = PreviewServer(camera)
            preview.start()
        display.show("Register", args.name)
        while len(embeddings) < args.samples and attempts < max_attempts:
            attempts += 1
            frame = camera.read()
            if frame is None:
                time.sleep(SAMPLE_INTERVAL_SECONDS)
                continue
            result = face_engine.extract_single_face(frame)
            if result["success"]:
                embeddings.append(result["embedding"])
                display.show("Sample", f"{len(embeddings)}/{args.samples}")
                print(f"Sample {len(embeddings)}/{args.samples}")
            else:
                display.show("Face invalid", result["status"])
                print(result["status"])
            time.sleep(SAMPLE_INTERVAL_SECONDS)

        if len(embeddings) < args.samples:
            raise SystemExit(f"Not enough samples: {len(embeddings)}/{args.samples}")

        embedding = np.mean(np.stack(embeddings), axis=0).astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        add_user(args.student_id, args.name, embedding)
        display.show("Registered", args.name)
        print(f"Registered {args.name} ({args.student_id})")
    finally:
        if preview is not None:
            preview.stop()
        camera.release()
        display.close()


if __name__ == "__main__":
    main()
