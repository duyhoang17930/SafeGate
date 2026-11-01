from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a small YOLO PPE detector.")
    parser.add_argument("--model", default="yolo11n.pt", help="Initial YOLO checkpoint.")
    parser.add_argument("--data", default="ppe.yaml", help="YOLO dataset YAML.")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default=None)
    parser.add_argument("--amp", action="store_true", help="Enable Ultralytics AMP checks/training.")
    parser.add_argument("--output", default="models/ppe_best.pt")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = YOLO(args.model)
    train_kwargs = {
        "data": args.data,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "patience": 20,
        "workers": 4,
        "amp": args.amp,
    }
    if args.device is not None:
        train_kwargs["device"] = args.device
    result = model.train(**train_kwargs)

    best = Path(result.save_dir) / "weights" / "best.pt"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(best.read_bytes())
    print(f"Copied best checkpoint to {output}")


if __name__ == "__main__":
    main()
