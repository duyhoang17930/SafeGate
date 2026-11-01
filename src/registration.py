from __future__ import annotations

import shutil
import time
from pathlib import Path

import cv2

from .camera import Camera
from .face_recognition import InsightFaceRecognizer


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_image_paths(paths: list[str | Path]) -> list[Path]:
    images: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            images.extend(
                sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
            )
        elif path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(path)
    return images


class FaceRegistrar:
    def __init__(
        self,
        recognizer: InsightFaceRecognizer,
        face_image_dir: str | Path,
    ) -> None:
        self.recognizer = recognizer
        self.face_image_dir = Path(face_image_dir)

    def register_from_files(self, name: str, paths: list[str | Path], copy_images: bool = True) -> int:
        image_paths = collect_image_paths(paths)
        if not image_paths:
            raise ValueError("No image files were provided")

        stored_paths = image_paths
        if copy_images:
            person_dir = self.face_image_dir / name
            person_dir.mkdir(parents=True, exist_ok=True)
            stored_paths = []
            for index, image_path in enumerate(image_paths, start=1):
                suffix = image_path.suffix.lower() or ".jpg"
                destination = person_dir / f"{index:03d}{suffix}"
                if image_path.resolve() != destination.resolve():
                    shutil.copy2(image_path, destination)
                stored_paths.append(destination)

        return self.recognizer.add_person_from_images(name, stored_paths)

    def capture_samples(
        self,
        name: str,
        camera_index: int,
        width: int,
        height: int,
        samples: int,
        delay_seconds: float = 0.5,
    ) -> list[Path]:
        person_dir = self.face_image_dir / name
        person_dir.mkdir(parents=True, exist_ok=True)
        saved: list[Path] = []

        with Camera(camera_index, width, height) as camera:
            while len(saved) < samples:
                frame = camera.read()
                preview = frame.copy()
                cv2.putText(
                    preview,
                    f"{name}: sample {len(saved) + 1}/{samples} - SPACE save, Q quit",
                    (16, 32),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("Register face", preview)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                if key == ord(" "):
                    output = person_dir / f"{int(time.time() * 1000)}.jpg"
                    cv2.imwrite(str(output), frame)
                    saved.append(output)
                    time.sleep(delay_seconds)

        cv2.destroyAllWindows()
        return saved

