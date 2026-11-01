from __future__ import annotations

from dataclasses import dataclass

from .detections import Detection, iou


@dataclass
class Track:
    track_id: int
    bbox: tuple[int, int, int, int]
    missing_frames: int = 0
    name: str = "Unknown"
    similarity: float = 0.0


class IoUTracker:
    def __init__(self, iou_threshold: float = 0.3, max_missing_frames: int = 15) -> None:
        self.iou_threshold = iou_threshold
        self.max_missing_frames = max_missing_frames
        self.next_id = 1
        self.tracks: dict[int, Track] = {}

    def update(self, detections: list[Detection]) -> list[Detection]:
        unmatched_tracks = set(self.tracks)
        for detection in detections:
            best_track_id: int | None = None
            best_iou = 0.0
            for track_id in list(unmatched_tracks):
                score = iou(detection.xyxy, self.tracks[track_id].bbox)
                if score > best_iou:
                    best_iou = score
                    best_track_id = track_id

            if best_track_id is not None and best_iou >= self.iou_threshold:
                track = self.tracks[best_track_id]
                track.bbox = detection.xyxy
                track.missing_frames = 0
                detection.track_id = best_track_id
                unmatched_tracks.remove(best_track_id)
            else:
                track_id = self.next_id
                self.next_id += 1
                self.tracks[track_id] = Track(track_id=track_id, bbox=detection.xyxy)
                detection.track_id = track_id

        for track_id in list(unmatched_tracks):
            track = self.tracks[track_id]
            track.missing_frames += 1
            if track.missing_frames > self.max_missing_frames:
                del self.tracks[track_id]

        return detections

    def set_identity(self, track_id: int, name: str, similarity: float) -> None:
        if track_id in self.tracks:
            self.tracks[track_id].name = name
            self.tracks[track_id].similarity = similarity

    def identity_for(self, track_id: int | None) -> tuple[str, float]:
        if track_id is None or track_id not in self.tracks:
            return "Unknown", 0.0
        track = self.tracks[track_id]
        return track.name, track.similarity

