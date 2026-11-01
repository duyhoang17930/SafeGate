# Lab 2: Same AI, Different Hardware

Created folder:

```text
raspberrypi_lab2_traffic_light
```

Keep the same rule as Lab 1, but use a traffic-light module instead of a servo.

Behavior:

```text
known face + helmet + vest -> green light
known face + missing PPE   -> yellow light + buzzer
unknown face               -> red light + buzzer
no face                    -> all lights off / wait silently
```

Why this is good:

```text
Lab 1: physical gate using servo
Lab 2: simple status indicator using traffic-light LEDs
```

Suggested hardware:

```text
Raspberry Pi
USB camera
traffic-light LED module or 3 LEDs
buzzer
LCD/OLED display
```
