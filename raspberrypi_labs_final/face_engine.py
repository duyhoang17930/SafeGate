import cv2
import numpy as np

from config import (
    FACE_MATCH_THRESHOLD,
    SFACE_MODEL,
    YUNET_MODEL,
    YUNET_NMS_THRESHOLD,
    YUNET_SCORE_THRESHOLD,
    YUNET_TOP_K,
)


class FaceEngine:
    def __init__(self) -> None:
        if not YUNET_MODEL.exists():
            raise FileNotFoundError(f"Missing YuNet model: {YUNET_MODEL}")
        if not SFACE_MODEL.exists():
            raise FileNotFoundError(f"Missing SFace model: {SFACE_MODEL}")

        self.detector = cv2.FaceDetectorYN.create(
            str(YUNET_MODEL),
            "",
            (320, 320),
            YUNET_SCORE_THRESHOLD,
            YUNET_NMS_THRESHOLD,
            YUNET_TOP_K,
        )
        self.recognizer = cv2.FaceRecognizerSF.create(str(SFACE_MODEL), "")

    def detect_faces(self, frame):
        height, width = frame.shape[:2]
        self.detector.setInputSize((width, height))
        _, faces = self.detector.detect(frame)
        return [] if faces is None else faces

    def get_embedding(self, frame, face) -> np.ndarray:
        aligned_face = self.recognizer.alignCrop(frame, face)
        feature = self.recognizer.feature(aligned_face)
        embedding = feature.flatten().astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding

    def extract_single_face(self, frame) -> dict:
        faces = self.detect_faces(frame)
        if len(faces) == 0:
            return {"success": False, "status": "NO_FACE", "message": "No face", "embedding": None}
        if len(faces) > 1:
            return {
                "success": False,
                "status": "MULTIPLE_FACES",
                "message": "Multiple faces",
                "embedding": None,
            }
        return {
            "success": True,
            "status": "OK",
            "message": "Face detected",
            "embedding": self.get_embedding(frame, faces[0]),
        }

    @staticmethod
    def similarity(embedding1, embedding2) -> float:
        if embedding1 is None or embedding2 is None:
            return 0.0
        embedding1 = np.asarray(embedding1, dtype=np.float32)
        embedding2 = np.asarray(embedding2, dtype=np.float32)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    def find_best_match(self, query_embedding, users: list[dict]) -> dict:
        best_user = None
        best_score = -1.0
        for user in users:
            score = self.similarity(query_embedding, user["embedding"])
            if score > best_score:
                best_score = score
                best_user = user

        if best_user is None:
            return {"matched": False, "user": None, "score": 0.0}

        matched = best_score >= FACE_MATCH_THRESHOLD
        return {
            "matched": matched,
            "user": best_user if matched else None,
            "score": best_score,
        }

