from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import time

import cv2
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bundled PPE detector on images, a folder, or a webcam."
    )
    parser.add_argument(
        "--source",
        default="0",
        help="Image/file folder path, or camera index (0 for the default webcam).",
    )
    parser.add_argument(
        "--model",
        default=str(ROOT / "models" / "ppe_best.onnx"),
        help="Path to a YOLO ONNX model.",
    )
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument(
        "--output",
        default=str(ROOT / "results"),
        help="Folder for annotated images and videos.",
    )
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def print_detections(result) -> None:
    print(f"\n{Path(result.path).name}:")
    if result.boxes is None or len(result.boxes) == 0:
        print("  No PPE objects detected.")
        return

    for box in result.boxes:
        class_id = int(box.cls[0].item())
        label = result.names.get(class_id, str(class_id))
        confidence = float(box.conf[0].item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        print(
            f"  {label}: {confidence:.2f} "
            f"(x1={x1:.0f}, y1={y1:.0f}, x2={x2:.0f}, y2={y2:.0f})"
        )


def run_camera(model: YOLO, camera_index: int, options: dict) -> None:
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise RuntimeError(
            f"Could not open camera {camera_index}. Check Windows camera permissions "
            "or try another index, such as --source 1."
        )

    window_name = "PPE Live Camera - press Q to quit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    last_log_time = 0.0
    print(f"Camera {camera_index} opened. Press Q in the video window to quit.")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Could not read a frame from the camera.")
                break

            result = model.predict(source=frame, **options)[0]
            detected = set()
            if result.boxes is not None:
                for class_id in result.boxes.cls.tolist():
                    class_id = int(class_id)
                    names = result.names
                    label = names.get(class_id, str(class_id)) if isinstance(names, dict) else names[class_id]
                    detected.add(str(label).lower())

            has_helmet = "helmet" in detected
            has_vest = "vest" in detected
            view = result.plot()

            cv2.rectangle(view, (0, 0), (view.shape[1], 76), (30, 30, 30), -1)
            helmet_color = (60, 220, 60) if has_helmet else (60, 80, 240)
            vest_color = (60, 220, 60) if has_vest else (60, 80, 240)
            helmet_text = "DETECTED" if has_helmet else "NOT DETECTED"
            vest_text = "DETECTED" if has_vest else "NOT DETECTED"
            cv2.putText(
                view,
                f"Helmet: {helmet_text}",
                (16, 31),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                helmet_color,
                2,
            )
            cv2.putText(
                view,
                f"Vest: {vest_text}",
                (16, 64),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                vest_color,
                2,
            )
            cv2.imshow(window_name, view)

            now = time.monotonic()
            if now - last_log_time >= 1.0:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(
                    f"[{timestamp}] Helmet: {helmet_text} | Vest: {vest_text}",
                    flush=True,
                )
                last_log_time = now

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


def main() -> None:
    args = parse_args()
    model_path = resolve_path(args.model)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = YOLO(str(model_path), task="detect")
    source_text = args.source.strip()
    is_camera = source_text.lower() in {"camera", "webcam"} or source_text.isdigit()

    options = {
        "imgsz": args.imgsz,
        "conf": args.conf,
        "iou": args.iou,
        "device": "cpu",
        "verbose": False,
    }

    if is_camera:
        camera_index = 0 if source_text.lower() in {"camera", "webcam"} else int(source_text)
        run_camera(model, camera_index, options)
        return

    source_path = resolve_path(source_text)
    if not source_path.exists():
        raise FileNotFoundError(f"Image or folder not found: {source_path}")
    if not source_path.is_file() and not source_path.is_dir():
        raise ValueError(f"Source must be an image or a folder: {source_path}")

    output_path = resolve_path(args.output)
    results = model.predict(
        source=str(source_path),
        save=True,
        project=str(output_path.parent),
        name=output_path.name,
        exist_ok=True,
        **options,
    )
    for result in results:
        print_detections(result)
    print(f"\nAnnotated results saved in: {output_path}")


if __name__ == "__main__":
    main()
