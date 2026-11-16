# Raspberry Pi Safety Access (Final)

Face recognition + PPE (helmet & vest) check that controls a door servo,
3 status LEDs, a buzzer and an I2C LCD.

## Behavior

```text
known face + helmet + vest -> LCD "Access granted", green LED, servo opens 90 degrees for 3 s
known face + missing PPE   -> LCD "PPE missing",    yellow LED + buzzer
unknown face               -> LCD "Access denied",  red LED + buzzer
no face                    -> LCD "Waiting face",   all outputs off, door locked
```

## Wiring (BCM numbering, see `config.py`)

| Device                        | Pin                         |
|-------------------------------|-----------------------------|
| Green LED (+ 220-330 ohm)     | GPIO 17                     |
| Yellow LED (+ 220-330 ohm)    | GPIO 23                     |
| Red LED (+ 220-330 ohm)       | GPIO 27                     |
| Active buzzer                 | GPIO 22                     |
| Servo signal (SG90/MG90)      | GPIO 18                     |
| LCD 16x2 I2C (PCF8574, 0x27)  | SDA = GPIO 2, SCL = GPIO 3  |
| USB camera                    | `/dev/video0`               |

Power the servo and the LCD from 5V and share GND with the Pi.
Enable I2C with `sudo raspi-config` -> Interface Options -> I2C, then check
the LCD with `i2cdetect -y 1` (should show `27`).

## Setup On Raspberry Pi

```bash
bash install_pi.sh
source .venv/bin/activate
```

The required models are already included in `models/`.

Register a user once:

```bash
python register_user.py --student-id 001 --name Huy
```

Run:

```bash
python main.py
```

When it starts, it opens a camera preview tab:

```text
http://127.0.0.1:8080
```

If the Raspberry Pi has no desktop browser, open this from another device on the same network:

```text
http://<raspberry-pi-ip>:8080
```

## Web dashboard

`main.py` also serves a JSON API on port 8080 (`/api/status`, `/api/logs`,
`/api/users`). The Next.js dashboard in [`dashboard/`](dashboard/README.md)
uses it to monitor the camera, LCD, LEDs, servo, buzzer and access log live:

```bash
cd dashboard && npm install && npm run dev
```

Open `http://localhost:3000` and enter `http://<raspberry-pi-ip>:8080`.
