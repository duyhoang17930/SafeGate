from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


class ViolationLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["timestamp", "track_id", "name", "helmet", "vest"])

    def log(self, track_id: int | None, name: str, helmet_ok: bool, vest_ok: bool) -> None:
        if helmet_ok and vest_ok:
            return
        with self.path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    datetime.now().isoformat(timespec="seconds"),
                    track_id or "",
                    name,
                    "OK" if helmet_ok else "MISSING",
                    "OK" if vest_ok else "MISSING",
                ]
            )

