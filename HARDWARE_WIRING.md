# Hardware Wiring Guide

This project uses **BCM GPIO numbers** in `raspberrypi_labs_final/config.py`.

## Common Hardware

USB camera:

```text
Plug into Raspberry Pi USB port
```

I2C LCD 16x2, address `0x27`:

```text
LCD VCC -> Raspberry Pi 5V
LCD GND -> Raspberry Pi GND
LCD SDA -> GPIO2  / physical pin 3
LCD SCL -> GPIO3  / physical pin 5
```

Enable I2C on Raspberry Pi:

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
```

Check LCD address:

```bash
i2cdetect -y 1
```

## Lab 1: Servo Gate

Used by:

```bash
python lab1.py
```

Servo SG90/MG90:

```text
Servo signal -> GPIO18 / physical pin 12
Servo VCC    -> external 5V power supply +
Servo GND    -> external 5V power supply -
Pi GND       -> external 5V power supply -
```

Important:

```text
Do not power the servo directly from Raspberry Pi 5V if the servo draws too much current.
Always connect Raspberry Pi GND and external power GND together.
```

Buzzer:

```text
Buzzer + -> GPIO22 / physical pin 15
Buzzer - -> GND
```

Optional LEDs:

```text
Green LED anode -> GPIO17 / physical pin 11 through 220 ohm resistor
Green LED cathode -> GND

Red LED anode -> GPIO27 / physical pin 13 through 220 ohm resistor
Red LED cathode -> GND
```

## Lab 2: Traffic Light

Used by:

```bash
python lab2.py
```

Traffic-light LED module or 3 separate LEDs:

```text
Green signal  -> GPIO17 / physical pin 11
Yellow signal -> GPIO23 / physical pin 16
Red signal    -> GPIO27 / physical pin 13
GND           -> Raspberry Pi GND
```

If using separate LEDs:

```text
GPIO pin -> 220 ohm resistor -> LED anode
LED cathode -> GND
```

Buzzer:

```text
Buzzer + -> GPIO22 / physical pin 15
Buzzer - -> GND
```

## Pin Summary

```text
GPIO2   physical pin 3   LCD SDA
GPIO3   physical pin 5   LCD SCL
GPIO17  physical pin 11  green LED / green traffic light
GPIO18  physical pin 12  servo signal
GPIO27  physical pin 13  red LED / red traffic light
GPIO22  physical pin 15  buzzer
GPIO23  physical pin 16  yellow traffic light
5V      physical pin 2/4 LCD VCC, external servo supply reference only
GND     physical pin 6/9/14/20/25/30/34/39
```

## Behavior

Lab 1:

```text
known face + helmet + vest -> servo opens 90 degrees
missing PPE / unknown face -> buzzer
```

Lab 2:

```text
known face + helmet + vest -> green light
known face + missing PPE   -> yellow light + buzzer
unknown face               -> red light + buzzer
```

