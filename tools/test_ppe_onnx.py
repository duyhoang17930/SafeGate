from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

import config
from src.ppe_detector import PPEDetector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a PPE model on an image or camera.")
    parser.add_argument("--model", default=str(config.PPE_MODEL_PATH))
    parser.add_argument("--source", default=None, help="Image path. Omit to use camera.")
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    parser.add_argument("--imgsz", type=int, default=config.PPE_IMAGE_SIZE)
    return parser.parse_args()


def draw(image, detections):
    for detection in detections:
        x1, y1, x2, y2 = detection.xyxy
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 180, 255), 2)
        cv2.putText(
            image,
            f"{detection.label} {detection.confidence:.2f}",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 180, 255),
            2,
        )
    return image


def main() -> None:
    args = parse_args()
    detector = PPEDetector(args.model, image_size=args.imgsz)

    if args.source:
        image_path = Path(args.source)
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        start = time.perf_counter()
        detections = detector.detect(image)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"Inference: {elapsed_ms:.1f} ms")
        for detection in detections:
            print(detection)
        cv2.imshow("PPE test", draw(image, detections))
        cv2.waitKey(0)
        return

    capture = cv2.VideoCapture(args.camera)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open camera {args.camera}")
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        start = time.perf_counter()
        detections = detector.detect(frame)
        elapsed_ms = (time.perf_counter() - start) * 1000
        frame = draw(frame, detections)
        cv2.putText(frame, f"{elapsed_ms:.1f} ms", (16, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("PPE test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

