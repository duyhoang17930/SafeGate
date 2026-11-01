from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export trained PPE YOLO model to ONNX.")
    parser.add_argument("--model", default="models/ppe_best.pt")
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--dynamic", action="store_true")
    parser.add_argument("--simplify", action="store_true", default=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = YOLO(str(model_path))
    output = model.export(
        format="onnx",
        imgsz=args.imgsz,
        simplify=args.simplify,
        dynamic=args.dynamic,
    )
    print(f"Exported ONNX model: {output}")


if __name__ == "__main__":
    main()

