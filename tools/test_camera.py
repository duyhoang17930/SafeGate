from __future__ import annotations

import argparse
import time

import cv2

import config
from src.camera import Camera


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview camera and report FPS.")
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    parser.add_argument("--width", type=int, default=config.CAMERA_WIDTH)
    parser.add_argument("--height", type=int, default=config.CAMERA_HEIGHT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frames = 0
    start = time.perf_counter()
    with Camera(args.camera, args.width, args.height) as camera:
        while True:
            frame = camera.read()
            frames += 1
            elapsed = max(time.perf_counter() - start, 1e-6)
            fps = frames / elapsed
            cv2.putText(
                frame,
                f"Camera FPS: {fps:.1f} | Q quit",
                (16, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Camera test", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

