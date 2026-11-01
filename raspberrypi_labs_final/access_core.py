import csv
import threading
import time
from datetime import datetime

import numpy as np

from camera import Camera
from config import (
    ACCESS_COOLDOWN_SECONDS,
    ACCESS_SAMPLES,
    DENIED_COOLDOWN_SECONDS,
    LOG_PATH,
    SAMPLE_INTERVAL_SECONDS,
)
from database import get_all_users, init_database
from display import Display
from face_engine import FaceEngine
from ppe_status import PPEStatus
from preview_server import PreviewServer
from config import PREVIEW_ENABLED


def append_log(status: str, name: str, score: float, detail: str = "") -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    exists = LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if not exists:
            writer.writerow(["timestamp", "status", "name", "score", "detail"])
        writer.writerow([datetime.now().isoformat(timespec="seconds"), status, name, f"{score:.4f}", detail])


def missing_ppe_text(status_map: dict) -> str:
    missing = []
    if not status_map.get("helmet"):
        missing.append("helmet")
    if not status_map.get("vest"):
        missing.append("vest")
    return ", ".join(missing)


def collect_face_embedding(camera: Camera, face_engine: FaceEngine, display: Display):
    embeddings = []
    last_status = "NO_FACE"
    attempts = 0
    max_attempts = ACCESS_SAMPLES * 6

    while len(embeddings) < ACCESS_SAMPLES and attempts < max_attempts:
        attempts += 1
        frame = camera.read()
        if frame is None:
            time.sleep(SAMPLE_INTERVAL_SECONDS)
            continue

        result = face_engine.extract_single_face(frame)
        if result["success"]:
            embeddings.append(result["embedding"])
            display.show("Scanning", f"{len(embeddings)}/{ACCESS_SAMPLES}")
        else:
            last_status = result["status"]
            if last_status == "NO_FACE":
                display.show("Waiting face", "")
            else:
                display.show("Scan failed", last_status)
        time.sleep(SAMPLE_INTERVAL_SECONDS)

    if len(embeddings) < ACCESS_SAMPLES:
        return None, last_status

    embedding = np.mean(np.stack(embeddings), axis=0).astype(np.float32)
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding, "OK"


def run_lab(hardware, title: str, use_yellow_for_ppe: bool) -> None:
    init_database()
    camera = Camera()
    face_engine = FaceEngine()
    display = Display()
    ppe = PPEStatus()
    preview = None

    if PREVIEW_ENABLED:
        preview = PreviewServer(camera)
        preview.start()

    display.show(title, "Ready")
    print(f"[SYSTEM] {title} started")

    try:
        while True:
            users = get_all_users()
            if not users:
                display.show("No users", "Register first")
                time.sleep(2)
                continue

            query_embedding, status = collect_face_embedding(camera, face_engine, display)
            if query_embedding is None:
                if status != "NO_FACE":
                    display.show("Access denied", status)
                    append_log("DENIED", "Unknown", 0.0, status)
                    threading.Thread(target=hardware.access_denied, daemon=True).start()
                    time.sleep(DENIED_COOLDOWN_SECONDS)
                continue

            match = face_engine.find_best_match(query_embedding, users)
            score = float(match["score"])

            if not match["matched"]:
                display.show("Access denied", f"Score {score:.2f}")
                append_log("DENIED", "Unknown", score, "LOW_SCORE")
                print(f"[DENIED] unknown score={score:.4f}")
                threading.Thread(target=hardware.access_denied, daemon=True).start()
                time.sleep(DENIED_COOLDOWN_SECONDS)
                continue

            user = match["user"]
            name = user["name"]
            frame = camera.read()
            if frame is None:
                display.show("Access denied", "Camera error")
                append_log("DENIED", name, score, "CAMERA_ERROR")
                threading.Thread(target=hardware.access_denied, daemon=True).start()
                time.sleep(DENIED_COOLDOWN_SECONDS)
                continue

            status_map = ppe.check(frame)
            detail = f"H:{status_map['helmet']} V:{status_map['vest']}"
            missing = missing_ppe_text(status_map)
            if missing:
                display.show("PPE missing", missing)
                append_log("DENIED", name, score, f"MISSING_{missing.upper()}")
                print(f"[DENIED] {name} missing={missing} score={score:.4f}")
                action = hardware.ppe_missing if use_yellow_for_ppe else hardware.access_denied
                threading.Thread(target=action, daemon=True).start()
                time.sleep(DENIED_COOLDOWN_SECONDS)
                continue

            display.show("Access granted", name)
            append_log("GRANTED", name, score, detail)
            print(f"[GRANTED] {name} score={score:.4f} {detail}")
            threading.Thread(target=hardware.access_granted, daemon=True).start()
            time.sleep(ACCESS_COOLDOWN_SECONDS)
    except KeyboardInterrupt:
        print("[SYSTEM] Stopping")
    finally:
        if preview is not None:
            preview.stop()
        camera.release()
        hardware.close()
        display.close()
