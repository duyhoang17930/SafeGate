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
)


class Hardware:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        try:
            from gpiozero import AngularServo, Buzzer, LED

            self.green_led = LED(GREEN_LED_PIN)
            self.red_led = LED(RED_LED_PIN)
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
            self.green_led = None
            self.red_led = None
            self.buzzer = None
            self.servo = None
            self.mock = True

        self.lock_door()

    def _led(self, led, enabled: bool) -> None:
        if led is not None:
            led.on() if enabled else led.off()

    def _buzzer(self, enabled: bool) -> None:
        if self.buzzer is not None:
            self.buzzer.on() if enabled else self.buzzer.off()

    def _servo_angle(self, angle: int) -> None:
        if self.servo is None:
            print(f"[SERVO] angle={angle}")
            return
        self.servo.angle = angle
        time.sleep(0.7)
        self.servo.detach()

    def lock_door(self) -> None:
        self._servo_angle(SERVO_LOCK_ANGLE)
        self._led(self.green_led, False)
        self._led(self.red_led, False)
        self._buzzer(False)

    def access_granted(self) -> None:
        with self.lock:
            self._led(self.red_led, False)
            self._buzzer(False)
            self._led(self.green_led, True)
            self._servo_angle(SERVO_OPEN_ANGLE)
            time.sleep(DOOR_OPEN_SECONDS)
            self._servo_angle(SERVO_LOCK_ANGLE)
            self._led(self.green_led, False)

    def access_denied(self) -> None:
        with self.lock:
            self._led(self.green_led, False)
            self._led(self.red_led, True)
            self._buzzer(True)
            time.sleep(DENIED_BUZZ_SECONDS)
            self._buzzer(False)
            self._led(self.red_led, False)

    def close(self) -> None:
        self.lock_door()
        for device in (self.green_led, self.red_led, self.buzzer, self.servo):
            if device is not None:
                device.close()

