import threading
import time

from config import (
    BUZZER_PIN,
    DENIED_BUZZ_SECONDS,
    GREEN_LED_PIN,
    GREEN_LIGHT_SECONDS,
    RED_LED_PIN,
    YELLOW_LED_PIN,
    YELLOW_LIGHT_SECONDS,
)


class Hardware:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        try:
            from gpiozero import Buzzer, LED

            self.green_led = LED(GREEN_LED_PIN)
            self.yellow_led = LED(YELLOW_LED_PIN)
            self.red_led = LED(RED_LED_PIN)
            self.buzzer = Buzzer(BUZZER_PIN)
        except Exception as error:
            print(f"[HARDWARE] GPIO unavailable, using mock mode: {error}")
            self.green_led = None
            self.yellow_led = None
            self.red_led = None
            self.buzzer = None

        self.all_off()

    def _led(self, led, enabled: bool) -> None:
        if led is not None:
            led.on() if enabled else led.off()

    def _buzzer(self, enabled: bool) -> None:
        if self.buzzer is not None:
            self.buzzer.on() if enabled else self.buzzer.off()

    def all_off(self) -> None:
        self._led(self.green_led, False)
        self._led(self.yellow_led, False)
        self._led(self.red_led, False)
        self._buzzer(False)

    def access_granted(self) -> None:
        with self.lock:
            self.all_off()
            self._led(self.green_led, True)
            print("[TRAFFIC] GREEN")
            time.sleep(GREEN_LIGHT_SECONDS)
            self._led(self.green_led, False)

    def ppe_missing(self) -> None:
        with self.lock:
            self.all_off()
            self._led(self.yellow_led, True)
            self._buzzer(True)
            print("[TRAFFIC] YELLOW")
            time.sleep(YELLOW_LIGHT_SECONDS)
            self._buzzer(False)
            self._led(self.yellow_led, False)

    def access_denied(self) -> None:
        with self.lock:
            self.all_off()
            self._led(self.red_led, True)
            self._buzzer(True)
            print("[TRAFFIC] RED")
            time.sleep(DENIED_BUZZ_SECONDS)
            self._buzzer(False)
            self._led(self.red_led, False)

    def close(self) -> None:
        self.all_off()
        for device in (self.green_led, self.yellow_led, self.red_led, self.buzzer):
            if device is not None:
                device.close()

