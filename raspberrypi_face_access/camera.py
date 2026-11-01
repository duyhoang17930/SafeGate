import time

import cv2

from config import CAMERA_BACKEND, CAMERA_DEVICE, FRAME_HEIGHT, FRAME_WIDTH


def _camera_source():
    if isinstance(CAMERA_DEVICE, int):
        return CAMERA_DEVICE
    text = str(CAMERA_DEVICE)
    return int(text) if text.isdigit() else text


class Camera:
    def __init__(self) -> None:
        backend = cv2.CAP_V4L2 if CAMERA_BACKEND.lower() == "v4l2" else cv2.CAP_ANY
        self.capture = cv2.VideoCapture(_camera_source(), backend)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        if not self.capture.isOpened():
            raise RuntimeError(f"Could not open camera: {CAMERA_DEVICE}")

        # Warm up the sensor.
        for _ in range(10):
            self.capture.read()
            time.sleep(0.05)

    def read(self):
        ok, frame = self.capture.read()
        if not ok or frame is None or frame.size == 0:
            return None
        return frame

    def release(self) -> None:
        self.capture.release()

