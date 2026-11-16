import csv
import json
import threading
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import cv2

from config import (
    DATABASE_PATH,
    LOG_PATH,
    PREVIEW_AUTO_OPEN,
    PREVIEW_HOST,
    PREVIEW_JPEG_QUALITY,
    PREVIEW_PORT,
)
from state import STATE


def read_logs(limit: int) -> list[dict]:
    if not LOG_PATH.exists():
        return []
    with LOG_PATH.open(newline="", encoding="utf-8") as fh:
        rows = deque(csv.DictReader(fh), maxlen=limit)
    return list(reversed(rows))


def read_users() -> list[dict]:
    if not DATABASE_PATH.exists():
        return []
    from database import get_connection

    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, student_id, name, created_at FROM users ORDER BY id"
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


class PreviewServer:
    def __init__(self, camera) -> None:
        self.camera = camera
        self.server = ThreadingHTTPServer((PREVIEW_HOST, PREVIEW_PORT), self._handler_class())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _handler_class(self):
        camera = self.camera

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return

            def _cors(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

            def _json(self, payload, status=200):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self._cors()
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self):
                self.send_response(204)
                self._cors()
                self.end_headers()

            def do_GET(self):
                url = urlparse(self.path)
                if url.path == "/api/status":
                    self._json(STATE.snapshot())
                    return
                if url.path == "/api/logs":
                    try:
                        limit = int(parse_qs(url.query).get("limit", ["100"])[0])
                    except ValueError:
                        limit = 100
                    self._json(read_logs(max(1, min(limit, 1000))))
                    return
                if url.path == "/api/users":
                    self._json(read_users())
                    return

                if self.path in ("/", "/index.html"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        b"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Camera Preview</title>
  <style>
    body { margin: 0; background: #111; color: white; font-family: Arial, sans-serif; }
    header { padding: 10px 14px; background: #222; }
    img { display: block; max-width: 100vw; max-height: calc(100vh - 44px); margin: 0 auto; }
  </style>
</head>
<body>
  <header>Raspberry Pi Camera Preview</header>
  <img src="/stream.mjpg">
</body>
</html>"""
                    )
                    return

                if url.path != "/stream.mjpg":
                    self.send_error(404)
                    return

                self.send_response(200)
                self.send_header("Age", "0")
                self.send_header("Cache-Control", "no-cache, private")
                self.send_header("Pragma", "no-cache")
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                self._cors()
                self.end_headers()

                while True:
                    frame = camera.read()
                    if frame is None:
                        time.sleep(0.05)
                        continue
                    ok, encoded = cv2.imencode(
                        ".jpg",
                        frame,
                        [int(cv2.IMWRITE_JPEG_QUALITY), PREVIEW_JPEG_QUALITY],
                    )
                    if not ok:
                        continue
                    data = encoded.tobytes()
                    try:
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n")
                        self.wfile.write(f"Content-Length: {len(data)}\r\n\r\n".encode("ascii"))
                        self.wfile.write(data)
                        self.wfile.write(b"\r\n")
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    time.sleep(0.04)

        return Handler

    def start(self) -> str:
        self.thread.start()
        url = f"http://127.0.0.1:{PREVIEW_PORT}"
        print(f"[PREVIEW] {url}")
        if PREVIEW_AUTO_OPEN:
            threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
        return url

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()

