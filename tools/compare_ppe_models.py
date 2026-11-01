from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

import config
from src.ppe_detector import PPEDetector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare PPE detections from two model exports.")
    parser.add_argument("image")
    parser.add_argument("--a", default=str(config.PPE_TRAINED_PT_PATH), help="First model path, usually PT.")
    parser.add_argument("--b", default=str(config.PPE_MODEL_PATH), help="Second model path, usually ONNX.")
    parser.add_argument("--imgsz", type=int, default=config.PPE_IMAGE_SIZE)
    return parser.parse_args()


def run(label: str, detector: PPEDetector, image):
    start = time.perf_counter()
    detections = detector.detect(image)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"{label}: {elapsed_ms:.1f} ms, {len(detections)} detections")
    for det in detections:
        print(f"  {det.label:8s} conf={det.confidence:.3f} box={det.xyxy}")


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    run("model A", PPEDetector(args.a, image_size=args.imgsz), image)
    run("model B", PPEDetector(args.b, image_size=args.imgsz), image)


if __name__ == "__main__":
    main()

