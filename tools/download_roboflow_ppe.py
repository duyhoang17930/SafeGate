from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from math import ceil

from roboflow import Roboflow


DEFAULT_CLASS_MAP = {
    "worker": "person",
    "person": "person",
    "helmet": "helmet",
    "vest": "vest",
    "reflectiveVest": "vest",
}

TARGET_NAMES = ["person", "helmet", "vest"]
TARGET_IDS = {name: idx for idx, name in enumerate(TARGET_NAMES)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a Roboflow PPE dataset and remap classes for this project."
    )
    parser.add_argument("--api-key", default=os.getenv("ROBOFLOW_API_KEY"))
    parser.add_argument("--workspace", default="v2-wo7jr")
    parser.add_argument("--project", default="ppe-construction-detection-dataset-utu1c")
    parser.add_argument("--version", type=int, default=12)
    parser.add_argument("--format", default="yolov11")
    parser.add_argument("--output", default="datasets/ppe")
    parser.add_argument("--raw-dir", default="datasets/roboflow_raw")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument(
        "--clear-output",
        action="store_true",
        help="Clear existing datasets/ppe images and labels before writing.",
    )
    return parser.parse_args()


def read_names(data_yaml: Path) -> list[str]:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("Install pyyaml or use the roboflow package dependencies.") from exc

    with data_yaml.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    names = data.get("names")
    if isinstance(names, dict):
        return [names[idx] for idx in sorted(names)]
    if isinstance(names, list):
        return names
    raise ValueError(f"Could not read class names from {data_yaml}")


def find_dataset_root(raw_dir: Path) -> Path:
    candidates = [p for p in raw_dir.rglob("data.yaml")]
    if not candidates:
        raise FileNotFoundError(f"No data.yaml found under {raw_dir}")
    return candidates[0].parent


def split_names(dataset_root: Path) -> list[str]:
    names = []
    for name in ("train", "valid", "val", "test"):
        if (dataset_root / name).exists():
            names.append(name)
    return names


def clear_output(output: Path) -> None:
    allowed = (output.resolve(),)
    for child in [output / "images", output / "labels"]:
        if child.exists():
            resolved = child.resolve()
            if not any(str(resolved).startswith(str(root)) for root in allowed):
                raise RuntimeError(f"Refusing to remove outside output directory: {resolved}")
            shutil.rmtree(child)


def copy_and_remap(dataset_root: Path, output: Path, val_ratio: float) -> None:
    source_names = read_names(dataset_root / "data.yaml")
    source_to_target_id: dict[int, int | None] = {}
    for source_id, source_name in enumerate(source_names):
        target_name = DEFAULT_CLASS_MAP.get(str(source_name))
        source_to_target_id[source_id] = TARGET_IDS[target_name] if target_name else None

    for split in split_names(dataset_root):
        target_split = "val" if split == "valid" else split
        image_src = dataset_root / split / "images"
        label_src = dataset_root / split / "labels"
        image_dst = output / "images" / target_split
        label_dst = output / "labels" / target_split
        image_dst.mkdir(parents=True, exist_ok=True)
        label_dst.mkdir(parents=True, exist_ok=True)

        if image_src.exists():
            for image_path in image_src.iterdir():
                if image_path.is_file():
                    shutil.copy2(image_path, image_dst / image_path.name)

        if label_src.exists():
            for label_path in label_src.glob("*.txt"):
                remapped_lines = []
                for line in label_path.read_text(encoding="utf-8").splitlines():
                    parts = line.strip().split()
                    if len(parts) != 5:
                        continue
                    source_id = int(float(parts[0]))
                    target_id = source_to_target_id.get(source_id)
                    if target_id is None:
                        continue
                    remapped_lines.append(" ".join([str(target_id), *parts[1:]]))
                (label_dst / label_path.name).write_text(
                    "\n".join(remapped_lines) + ("\n" if remapped_lines else ""),
                    encoding="utf-8",
                )

    ensure_validation_split(output, val_ratio=val_ratio)

    dataset_path = output.resolve().as_posix()
    (output / "data.yaml").write_text(
        f"path: {dataset_path}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "names:\n"
        "  0: person\n"
        "  1: helmet\n"
        "  2: vest\n",
        encoding="utf-8",
    )


def ensure_validation_split(output: Path, val_ratio: float) -> None:
    train_images = output / "images" / "train"
    train_labels = output / "labels" / "train"
    val_images = output / "images" / "val"
    val_labels = output / "labels" / "val"
    val_images.mkdir(parents=True, exist_ok=True)
    val_labels.mkdir(parents=True, exist_ok=True)

    existing_val = [p for p in val_images.iterdir() if p.is_file() and p.suffix.lower() != ".gitkeep"]
    if existing_val:
        return

    images = sorted(
        p for p in train_images.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    if len(images) < 2:
        return

    val_count = max(1, ceil(len(images) * val_ratio))
    for image_path in images[-val_count:]:
        label_path = train_labels / f"{image_path.stem}.txt"
        shutil.move(str(image_path), val_images / image_path.name)
        if label_path.exists():
            shutil.move(str(label_path), val_labels / label_path.name)


def main() -> None:
    args = parse_args()
    if not args.api_key:
        raise SystemExit("Missing API key. Set ROBOFLOW_API_KEY or pass --api-key.")

    raw_dir = Path(args.raw_dir)
    output = Path(args.output)
    raw_dir.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)

    if args.clear_output:
        clear_output(output)

    rf = Roboflow(api_key=args.api_key)
    project = rf.workspace(args.workspace).project(args.project)
    version = project.version(args.version)
    dataset = version.download(args.format, location=str(raw_dir / args.project))

    dataset_root = find_dataset_root(Path(dataset.location))
    copy_and_remap(dataset_root, output, args.val_ratio)
    print(f"Downloaded raw dataset to: {dataset_root}")
    print(f"Prepared remapped dataset at: {output}")
    print("Train with: python tools/train_ppe.py --data datasets/ppe/data.yaml")


if __name__ == "__main__":
    main()
