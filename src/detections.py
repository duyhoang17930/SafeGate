from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class Detection:
    label: str
    confidence: float
    xyxy: tuple[int, int, int, int]
    track_id: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def area(self) -> int:
        x1, y1, x2, y2 = self.xyxy
        return max(0, x2 - x1) * max(0, y2 - y1)

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.xyxy
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def crop(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        x1, y1, x2, y2 = self.xyxy
        x1 = max(0, min(w, x1))
        x2 = max(0, min(w, x2))
        y1 = max(0, min(h, y1))
        y2 = max(0, min(h, y2))
        return image[y1:y2, x1:x2]


def iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    x1 = max(ax1, bx1)
    y1 = max(ay1, by1)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter
    if union <= 0:
        return 0.0
    return inter / union


def center_inside(inner: Detection, outer: Detection) -> bool:
    cx, cy = inner.center
    x1, y1, x2, y2 = outer.xyxy
    return x1 <= cx <= x2 and y1 <= cy <= y2

