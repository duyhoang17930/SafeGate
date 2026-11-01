from __future__ import annotations

import cv2

import config

from .detections import Detection, center_inside
from .face_recognition import InsightFaceRecognizer
from .ppe_detector import PPEDetector
from .tracker import IoUTracker
from .violation_logger import ViolationLogger


class SafetyPipeline:
    def __init__(
        self,
        ppe_detector: PPEDetector,
        face_recognizer: InsightFaceRecognizer,
        tracker: IoUTracker,
        violation_logger: ViolationLogger,
    ) -> None:
        self.ppe_detector = ppe_detector
        self.face_recognizer = face_recognizer
        self.tracker = tracker
        self.violation_logger = violation_logger
        self.frame_index = 0
        self.last_detections: list[Detection] = []

    @classmethod
    def from_config(cls) -> "SafetyPipeline":
        return cls(
            ppe_detector=PPEDetector(
                config.PPE_MODEL_PATH,
                image_size=config.PPE_IMAGE_SIZE,
                confidence=config.PPE_CONFIDENCE_THRESHOLD,
                iou=config.PPE_IOU_THRESHOLD,
            ),
            face_recognizer=InsightFaceRecognizer(
                config.FACE_MODEL_NAME,
                config.FACE_DETECTION_SIZE,
                config.FACE_DB_PATH,
                config.FACE_SIMILARITY_THRESHOLD,
            ),
            tracker=IoUTracker(config.TRACK_IOU_THRESHOLD, config.TRACK_MAX_MISSING_FRAMES),
            violation_logger=ViolationLogger(config.VIOLATION_LOG_PATH),
        )

    def process(self, frame):
        self.frame_index += 1
        if self.frame_index == 1 or self.frame_index % config.PPE_EVERY_N_FRAMES == 0:
            self.last_detections = self.ppe_detector.detect(frame)

        persons = [d for d in self.last_detections if d.label == config.PPE_PERSON_CLASS]
        helmets = [d for d in self.last_detections if d.label == config.PPE_HELMET_CLASS]
        vests = [d for d in self.last_detections if d.label == config.PPE_VEST_CLASS]
        persons = self.tracker.update(persons)

        summaries = []
        for person in persons:
            name, similarity = self.tracker.identity_for(person.track_id)
            if self.frame_index == 1 or self.frame_index % config.FACE_EVERY_N_FRAMES == 0:
                crop = person.crop(frame)
                if crop.size:
                    match = self.face_recognizer.recognize_largest_face(crop)
                    if person.track_id is not None:
                        self.tracker.set_identity(person.track_id, match.name, match.similarity)
                    name, similarity = match.name, match.similarity

            helmet_ok = any(center_inside(helmet, person) for helmet in helmets)
            vest_ok = any(center_inside(vest, person) for vest in vests)
            self.violation_logger.log(person.track_id, name, helmet_ok, vest_ok)
            summaries.append(
                {
                    "track_id": person.track_id,
                    "name": name,
                    "similarity": similarity,
                    "helmet_ok": helmet_ok,
                    "vest_ok": vest_ok,
                    "bbox": person.xyxy,
                }
            )

        return summaries

    @staticmethod
    def draw(frame, summaries):
        for item in summaries:
            x1, y1, x2, y2 = item["bbox"]
            color = (0, 180, 0) if item["helmet_ok"] and item["vest_ok"] else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = (
                f"ID {item['track_id']} | {item['name']} | "
                f"H:{'OK' if item['helmet_ok'] else 'MISS'} "
                f"V:{'OK' if item['vest_ok'] else 'MISS'}"
            )
            cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        return frame

