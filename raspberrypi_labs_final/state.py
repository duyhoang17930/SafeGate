"""Thread-safe live state of the whole system, served to the dashboard."""

import copy
import threading
import time

from config import (
    BUZZER_PIN,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    GREEN_LED_PIN,
    LCD_COLUMNS,
    LCD_I2C_ADDRESS,
    LCD_ROWS,
    RED_LED_PIN,
    SERVO_LOCK_ANGLE,
    SERVO_PIN,
    YELLOW_LED_PIN,
)


class SystemState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data = {
            "system": {
                "title": "Safety Access",
                "phase": "starting",
                "started_at": time.time(),
                "hardware_mock": True,
                "users": 0,
            },
            "devices": {
                "green_led": {"on": False, "pin": GREEN_LED_PIN},
                "yellow_led": {"on": False, "pin": YELLOW_LED_PIN},
                "red_led": {"on": False, "pin": RED_LED_PIN},
                "buzzer": {"on": False, "pin": BUZZER_PIN},
                "servo": {"angle": SERVO_LOCK_ANGLE, "pin": SERVO_PIN, "door": "locked"},
                "lcd": {
                    "connected": False,
                    "address": f"0x{LCD_I2C_ADDRESS:02X}",
                    "cols": LCD_COLUMNS,
                    "rows": LCD_ROWS,
                    "lines": ["", ""],
                },
                "camera": {
                    "online": False,
                    "width": FRAME_WIDTH,
                    "height": FRAME_HEIGHT,
                    "last_frame_at": None,
                },
            },
            "last_event": None,
            "counters": {"granted": 0, "ppe_missing": 0, "denied": 0},
        }

    def set_system(self, **fields) -> None:
        with self._lock:
            self._data["system"].update(fields)

    def set_device(self, name: str, **fields) -> None:
        with self._lock:
            self._data["devices"][name].update(fields)

    def record_event(self, event: dict, counter: str) -> None:
        with self._lock:
            self._data["last_event"] = event
            self._data["counters"][counter] += 1

    def snapshot(self) -> dict:
        with self._lock:
            data = copy.deepcopy(self._data)
        now = time.time()
        data["server_time"] = now
        data["system"]["uptime_s"] = round(now - data["system"]["started_at"], 1)
        return data


STATE = SystemState()
