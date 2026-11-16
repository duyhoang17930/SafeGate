import threading
import time

from config import (
    BUZZER_PIN,
    DENIED_BUZZ_SECONDS,
    DOOR_OPEN_SECONDS,
    GREEN_LED_PIN,
    RED_LED_PIN,
    SERVO_LOCK_ANGLE,
    SERVO_OPEN_ANGLE,
    SERVO_PIN,
    YELLOW_BUZZ_SECONDS,
    YELLOW_LED_PIN,
)
from state import STATE

LED_NAMES = ("green_led", "yellow_led", "red_led")


class Hardware:
    """Green/yellow/red LEDs, buzzer and door servo.

    granted     -> green LED on + servo opens the door
    ppe missing -> yellow LED + buzzer
    denied      -> red LED + buzzer
    """

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.leds = {name: None for name in LED_NAMES}
        self.buzzer = None
        self.servo = None
        try:
            from gpiozero import AngularServo, Buzzer, LED

            self.leds = {
                "green_led": LED(GREEN_LED_PIN),
                "yellow_led": LED(YELLOW_LED_PIN),
                "red_led": LED(RED_LED_PIN),
            }
            self.buzzer = Buzzer(BUZZER_PIN)
            self.servo = AngularServo(
                SERVO_PIN,
                min_angle=0,
                max_angle=180,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
                initial_angle=None,
            )
            self.mock = False
        except Exception as error:
            print(f"[HARDWARE] GPIO unavailable, using mock mode: {error}")
            self.mock = True

        STATE.set_system(hardware_mock=self.mock)
        self.all_off()
        self._servo_angle(SERVO_LOCK_ANGLE)

    def _led(self, name: str, enabled: bool) -> None:
        led = self.leds[name]
        if led is not None:
            led.on() if enabled else led.off()
        STATE.set_device(name, on=enabled)

    def _buzzer(self, enabled: bool) -> None:
        if self.buzzer is not None:
            self.buzzer.on() if enabled else self.buzzer.off()
        STATE.set_device("buzzer", on=enabled)

    def _servo_angle(self, angle: int) -> None:
        door = "open" if angle == SERVO_OPEN_ANGLE else "locked"
        STATE.set_device("servo", angle=angle, door=door)
        if self.servo is None:
            print(f"[SERVO] angle={angle}")
            return
        self.servo.angle = angle
        time.sleep(0.7)
        # Stop sending pulses so the servo does not jitter while idle.
        self.servo.detach()

    def all_off(self) -> None:
        for name in LED_NAMES:
            self._led(name, False)
        self._buzzer(False)

    def access_granted(self) -> None:
        with self.lock:
            self.all_off()
            self._led("green_led", True)
            print("[HARDWARE] GREEN + door open")
            self._servo_angle(SERVO_OPEN_ANGLE)
            time.sleep(DOOR_OPEN_SECONDS)
            self._servo_angle(SERVO_LOCK_ANGLE)
            self._led("green_led", False)

    def ppe_missing(self) -> None:
        with self.lock:
            self.all_off()
            self._led("yellow_led", True)
            self._buzzer(True)
            print("[HARDWARE] YELLOW + buzzer")
            time.sleep(YELLOW_BUZZ_SECONDS)
            self._buzzer(False)
            self._led("yellow_led", False)

    def access_denied(self) -> None:
        with self.lock:
            self.all_off()
            self._led("red_led", True)
            self._buzzer(True)
            print("[HARDWARE] RED + buzzer")
            time.sleep(DENIED_BUZZ_SECONDS)
            self._buzzer(False)
            self._led("red_led", False)

    def close(self) -> None:
        with self.lock:
            self.all_off()
            self._servo_angle(SERVO_LOCK_ANGLE)
        for device in (*self.leds.values(), self.buzzer, self.servo):
            if device is not None:
                device.close()
