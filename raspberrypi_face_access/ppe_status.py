from config import PPE_CONFIDENCE, PPE_IMAGE_SIZE, PPE_MODEL


class PPEStatus:
    def __init__(self) -> None:
        if not PPE_MODEL.exists():
            raise FileNotFoundError(f"Missing PPE model: {PPE_MODEL}")
        from ultralytics import YOLO

        self.model = YOLO(str(PPE_MODEL))

    def check(self, frame) -> dict:
        result = self.model.predict(
            frame,
            imgsz=PPE_IMAGE_SIZE,
            conf=PPE_CONFIDENCE,
            verbose=False,
        )[0]
        labels = []
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                labels.append(str(result.names.get(cls_id, cls_id)))
        return {
            "person": "person" in labels,
            "helmet": "helmet" in labels,
            "vest": "vest" in labels,
        }

