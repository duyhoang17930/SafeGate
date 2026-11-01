from __future__ import annotations

from pathlib import Path

from ultralytics import YOLO

from .detections import Detection


class PPEDetector:
    def __init__(
        self,
        model_path: str | Path,
        image_size: int = 320,
        confidence: float = 0.35,
        iou: float = 0.45,
    ) -> None:
        self.model_path = Path(model_path)
        self.image_size = image_size
        self.confidence = confidence
        self.iou = iou
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"PPE model not found: {self.model_path}. Train/export a model first."
            )
        self.model = YOLO(str(self.model_path))

    def detect(self, image) -> list[Detection]:
        results = self.model.predict(
            image,
            imgsz=self.image_size,
            conf=self.confidence,
            iou=self.iou,
            verbose=False,
        )
        detections: list[Detection] = []
        if not results:
            return detections

        result = results[0]
        names = result.names
        boxes = result.boxes
        if boxes is None:
            return detections

        for box in boxes:
            cls_id = int(box.cls[0].item())
            label = str(names.get(cls_id, cls_id))
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int).tolist()
            detections.append(Detection(label=label, confidence=conf, xyxy=(x1, y1, x2, y2)))
        return detections

