# Wiring Guide (final version)

All pin numbers are **BCM GPIO numbers**, as set in `config.py`.
"Pin" means the physical pin on the 40-pin header (pin 1 is the corner pin next to the SD card side, marked with a square pad).

## Parts

| Qty | Part                                   | Notes                                   |
|-----|----------------------------------------|-----------------------------------------|
| 1   | Raspberry Pi (3B+/4/5)                 | Raspberry Pi OS Bookworm                |
| 1   | USB webcam                             | any UVC/V4L2 camera                     |
| 1   | LCD 16x2 with I2C backpack (PCF8574)   | address `0x27`                          |
| 3   | LEDs: green, yellow, red               |                                         |
| 3   | 220–330 Ω resistors                    | one per LED                             |
| 1   | Active buzzer (3.3–5 V)                | active = beeps with plain DC            |
| 1   | Servo SG90 / MG90S                     |                                         |
| 1   | External 5 V supply (≥1 A) for servo   | recommended; see servo section          |
| –   | Breadboard + jumper wires              |                                         |

## Pin summary

| Device         | Device pin       | Raspberry Pi            |
|----------------|------------------|-------------------------|
| LCD            | VCC              | 5V  (pin 2)             |
| LCD            | GND              | GND (pin 39)            |
| LCD            | SDA              | GPIO19 (pin 35) — software I2C bus 3 |
| LCD            | SCL              | GPIO26 (pin 37) — software I2C bus 3 |
| Green LED      | anode (+, long leg)  | GPIO17 (pin 11) via resistor |
| Red LED        | anode (+, long leg)  | GPIO27 (pin 13) via resistor |
| Yellow LED     | anode (+, long leg)  | GPIO23 (pin 16) via resistor |
| All LEDs       | cathode (−, short leg) | GND (pin 14)          |
| Buzzer         | +                | GPIO22 (pin 15)         |
| Buzzer         | −                | GND (pin 9)             |
| Servo          | signal (orange/yellow) | GPIO18 (pin 12)   |
| Servo          | VCC (red)        | external 5V + (or Pi 5V pin 4, see below) |
| Servo          | GND (brown/black)| external 5V − **and** Pi GND (pin 20)     |
| Camera         | USB              | any USB port            |

## Header layout (used pins marked)

```text
                 3V3  (1) (2)  5V   <- LCD VCC
               GPIO2  (3) (4)  5V   <- servo VCC (only without external supply)
               GPIO3  (5) (6)  GND
               GPIO4  (7) (8)  GPIO14
  Buzzer - ->    GND  (9) (10) GPIO15
 Green LED -> GPIO17 (11) (12) GPIO18 <- servo signal
   Red LED -> GPIO27 (13) (14) GND    <- LED cathodes
  Buzzer + -> GPIO22 (15) (16) GPIO23 <- yellow LED
                 3V3 (17) (18) GPIO24
              GPIO10 (19) (20) GND    <- servo / external supply GND
               GPIO9 (21) (22) GPIO25
              GPIO11 (23) (24) GPIO8
                 GND (25) (26) GPIO7
               GPIO0 (27) (28) GPIO1
               GPIO5 (29) (30) GND
               GPIO6 (31) (32) GPIO12
              GPIO13 (33) (34) GND
   LCD SDA -> GPIO19 (35) (36) GPIO16
   LCD SCL -> GPIO26 (37) (38) GPIO20
   LCD GND ->    GND (39) (40) GPIO21
```

GPIO2/GPIO3 (pins 3 and 5) are left free. To go back to hardware I2C, see the LCD section below.

## Wiring each part

### LCD 16x2 (I2C)

```text
LCD VCC -> 5V     (pin 2)
LCD GND -> GND    (pin 39)
LCD SDA -> GPIO19 (pin 35)
LCD SCL -> GPIO26 (pin 37)
```

GPIO19/GPIO26 are not hardware I2C pins, so the LCD runs on a **software I2C bus** (`/dev/i2c-3`)
created by the `i2c-gpio` overlay. Add this at the end of `/boot/firmware/config.txt`,
under an `[all]` line (not inside a `[cm4]`/`[pi5]` section), then reboot:

```text
[all]
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=19,i2c_gpio_scl=26
```

The code uses this bus through `LCD_I2C_PORT = 3` in `config.py`.

To test without rebooting (lasts until the next reboot):

```bash
sudo dtoverlay i2c-gpio bus=3 i2c_gpio_sda=19 i2c_gpio_scl=26
```

If you see `Failed to apply overlay '1_i2c-gpio'`, the overlay is already loaded
(check with `sudo dtoverlay -l`); bus 3 still works.

**Back to hardware I2C** (SDA GPIO2 pin 3, SCL GPIO3 pin 5): move the two wires, remove the
`dtoverlay=i2c-gpio...` line, set `LCD_I2C_PORT = 1` and use `i2cdetect -y 1`.

Turn the blue potentiometer on the back of the backpack if the screen is lit but shows no text (contrast).

### LEDs (x3)

Each LED gets its own resistor:

```text
GPIO pin -> 220 Ω resistor -> LED anode (long leg)
LED cathode (short leg) -> GND rail -> GND (pin 14)

Green  : GPIO17 (pin 11)
Yellow : GPIO23 (pin 16)
Red    : GPIO27 (pin 13)
```

A ready-made traffic-light LED module (R/Y/G/GND pins) can be used instead; it already has resistors, so connect its pins directly.

### Buzzer

```text
Buzzer + (long leg / red) -> GPIO22 (pin 15)
Buzzer -                  -> GND    (pin 9)
```

Use an **active** buzzer: the code only switches the pin on/off. A passive buzzer will just click.
For a loud buzzer that draws more than ~15 mA, drive it through an NPN transistor (e.g. 2N2222 + 1 kΩ base resistor) instead of straight from the GPIO pin.

### Servo (door lock)

```text
Servo signal (orange/yellow) -> GPIO18 (pin 12)
Servo VCC    (red)           -> external 5V supply +
Servo GND    (brown/black)   -> external 5V supply −
External supply −            -> Pi GND (pin 20)   <- shared ground is required
```

- 0° = locked, 90° = open (`SERVO_LOCK_ANGLE` / `SERVO_OPEN_ANGLE` in `config.py`).
- A single SG90 with no load *can* run from the Pi 5V pin (pin 4) for testing, but its current spikes may reset the Pi or corrupt the SD card. Use an external supply for the final setup.
- Never connect servo VCC to a 3.3V pin.

### USB camera

Plug into any USB port. Check it is detected:

```bash
ls /dev/video*        # expect /dev/video0
```

If it shows up under another number, change `CAMERA_DEVICE` in `config.py`.

## Enable and check

```bash
# 1. Software I2C bus for the LCD (see LCD section), then reboot
grep i2c-gpio /boot/firmware/config.txt
ls /dev/i2c*               # expect /dev/i2c-3

# 2. LCD should appear at 27
i2cdetect -y 3

# 3. Run
source .venv/bin/activate
python main.py
```

On start the log must **not** contain these lines; if it does, check the wiring for that part:

```text
[HARDWARE] GPIO unavailable, using mock mode: ...   -> LEDs / buzzer / servo not driven
[DISPLAY] LCD unavailable, using console: ...       -> LCD not found on I2C
Could not open camera: 0                            -> camera not detected
```

If `i2cdetect -y 3` shows an empty grid:

1. Check SDA is on **physical pin 35** and SCL on **physical pin 37** (pin number ≠ GPIO number).
2. Try swapping SDA and SCL.
3. Enable the internal pull-ups and scan again: `sudo pinctrl set 19,26 pu`.
4. Still empty? Move the LCD back to GPIO2/3 and run `i2cdetect -y 1` to check the LCD itself.
5. If it shows `3f` instead of `27`, set `LCD_I2C_ADDRESS = 0x3F` in `config.py`.

The web dashboard also shows `GPIO mock mode` and `Console fallback` badges in these cases.

## Expected behavior

```text
known face + helmet + vest -> LCD "Access granted", green LED, servo opens 90° for 3 s
known face + missing PPE   -> LCD "PPE missing",    yellow LED + buzzer 2 s
unknown face               -> LCD "Access denied",  red LED + buzzer 1.5 s
no face                    -> LCD "Waiting face",   all off, door locked
```

## Safety notes

- Wire with the Pi powered off.
- GPIO pins are 3.3 V and are not 5 V tolerant: never connect a 5 V signal to a GPIO input.
- Most PCF8574 LCD backpacks have pull-ups to their VCC. They normally work on 5 V with a Pi, but if you want to be strict, remove the backpack's SDA/SCL pull-up resistors or use an I2C level shifter.
- Keep all grounds (Pi, LEDs, buzzer, LCD, external supply) connected together.
