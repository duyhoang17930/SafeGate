from __future__ import annotations

import argparse

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test pretrained YOLO person detection.")
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--source", default="0", help="Camera index or image/video path.")
    parser.add_argument("--imgsz", type=int, default=320)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = int(args.source) if args.source.isdigit() else args.source
    model = YOLO(args.model)
    model.predict(source=source, imgsz=args.imgsz, classes=[0], show=True)


if __name__ == "__main__":
    main()

