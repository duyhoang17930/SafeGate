from __future__ import annotations

import argparse
import time

import cv2
import psutil

import config
from src.camera import Camera
from src.face_recognition import InsightFaceRecognizer
from src.ppe_detector import PPEDetector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark PPE and face inference on real hardware.")
    parser.add_argument("--model", default=str(config.PPE_MODEL_PATH), help="PT, ONNX, or NCNN model path.")
    parser.add_argument("--frames", type=int, default=300)
    parser.add_argument("--imgsz", type=int, default=config.PPE_IMAGE_SIZE)
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    parser.add_argument("--width", type=int, default=config.CAMERA_WIDTH)
    parser.add_argument("--height", type=int, default=config.CAMERA_HEIGHT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    detector = PPEDetector(args.model, image_size=args.imgsz)
    recognizer = InsightFaceRecognizer(
        config.FACE_MODEL_NAME,
        config.FACE_DETECTION_SIZE,
        config.FACE_DB_PATH,
        config.FACE_SIMILARITY_THRESHOLD,
    )
    yolo_times = []
    face_times = []
    start = time.perf_counter()

    with Camera(args.camera, args.width, args.height) as camera:
        for _ in range(args.frames):
            frame = camera.read()
            t0 = time.perf_counter()
            detector.detect(frame)
            yolo_times.append((time.perf_counter() - t0) * 1000)

            t0 = time.perf_counter()
            recognizer.recognize_largest_face(frame)
            face_times.append((time.perf_counter() - t0) * 1000)

    elapsed = time.perf_counter() - start
    process = psutil.Process()
    print(f"Model: {args.model}")
    print(f"Resolution: {args.imgsz}")
    print(f"Frames: {args.frames}")
    print()
    print(f"Average YOLO inference: {sum(yolo_times) / len(yolo_times):.1f} ms")
    print(f"Average face recognition: {sum(face_times) / len(face_times):.1f} ms")
    print(f"Pipeline FPS: {args.frames / elapsed:.2f}")
    print(f"CPU usage: {psutil.cpu_percent(interval=1):.1f} %")
    print(f"RAM: {process.memory_info().rss / (1024 * 1024):.1f} MB")


if __name__ == "__main__":
    main()

