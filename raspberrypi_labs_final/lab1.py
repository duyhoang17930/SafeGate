from access_core import run_lab
from hardware_servo import Hardware


if __name__ == "__main__":
    run_lab(
        hardware=Hardware(),
        title="Lab1 Servo",
        use_yellow_for_ppe=False,
    )

