from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis


@dataclass(slots=True)
class FaceMatch:
    name: str
    similarity: float
    bbox: tuple[int, int, int, int] | None = None


class InsightFaceRecognizer:
    def __init__(
        self,
        model_name: str,
        detection_size: tuple[int, int],
        db_path: str | Path,
        threshold: float,
    ) -> None:
        self.model_name = model_name
        self.detection_size = detection_size
        self.db_path = Path(db_path)
        self.threshold = threshold
        self.app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=-1, det_size=detection_size)
        self.face_db = self.load_database()

    def load_database(self) -> dict[str, np.ndarray]:
        if not self.db_path.exists():
            return {}
        with self.db_path.open("rb") as fh:
            raw = pickle.load(fh)
        return {name: self.normalize(np.asarray(vec, dtype=np.float32)) for name, vec in raw.items()}

    def save_database(self, face_db: dict[str, np.ndarray] | None = None) -> None:
        data = face_db if face_db is not None else self.face_db
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.db_path.open("wb") as fh:
            pickle.dump(data, fh)

    @staticmethod
    def normalize(embedding: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(embedding)
        if norm == 0:
            raise ValueError("Cannot normalize a zero-length embedding")
        return embedding / norm

    def extract_faces(self, image) -> list:
        return self.app.get(image)

    def extract_embeddings_from_image(self, image_path: str | Path) -> list[np.ndarray]:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        faces = self.extract_faces(image)
        return [self.normalize(face.embedding.astype(np.float32)) for face in faces]

    def embed_largest_face(self, image) -> tuple[np.ndarray, tuple[int, int, int, int]] | None:
        faces = self.extract_faces(image)
        if not faces:
            return None
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        bbox = tuple(face.bbox.astype(int).tolist())
        return self.normalize(face.embedding.astype(np.float32)), bbox

    def match_embedding(self, embedding: np.ndarray) -> FaceMatch:
        if not self.face_db:
            return FaceMatch("Unknown", 0.0)
        query = self.normalize(embedding.astype(np.float32))
        best_name = "Unknown"
        best_similarity = -1.0
        for name, stored in self.face_db.items():
            similarity = float(np.dot(query, stored))
            if similarity > best_similarity:
                best_name = name
                best_similarity = similarity
        if best_similarity < self.threshold:
            best_name = "Unknown"
        return FaceMatch(best_name, best_similarity)

    def recognize_largest_face(self, image) -> FaceMatch:
        embedded = self.embed_largest_face(image)
        if embedded is None:
            return FaceMatch("Unknown", 0.0)
        embedding, bbox = embedded
        match = self.match_embedding(embedding)
        match.bbox = bbox
        return match

    def add_person_from_images(self, name: str, image_paths: list[str | Path]) -> int:
        embeddings: list[np.ndarray] = []
        for image_path in image_paths:
            image_embeddings = self.extract_embeddings_from_image(image_path)
            if len(image_embeddings) != 1:
                print(f"Skipping {image_path}: expected 1 face, found {len(image_embeddings)}")
                continue
            embeddings.append(image_embeddings[0])

        if not embeddings:
            raise ValueError(f"No valid single-face images found for {name}")

        person_embedding = np.mean(np.stack(embeddings), axis=0)
        self.face_db[name] = self.normalize(person_embedding.astype(np.float32))
        self.save_database()
        return len(embeddings)

