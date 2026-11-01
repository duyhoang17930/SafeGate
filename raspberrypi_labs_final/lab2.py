from access_core import run_lab
from hardware_traffic import Hardware


if __name__ == "__main__":
    run_lab(
        hardware=Hardware(),
        title="Lab2 Traffic",
        use_yellow_for_ppe=True,
    )

