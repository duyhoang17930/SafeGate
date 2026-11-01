# Raspberry Pi Labs

One folder, two lab run files.

## Lab 1

```bash
python lab1.py
```

Behavior:

```text
known face + helmet + vest -> servo opens 90 degrees
known face + missing PPE   -> buzzer
unknown face               -> buzzer
no face                    -> waits silently
```

## Lab 2

```bash
python lab2.py
```

Behavior:

```text
known face + helmet + vest -> green light
known face + missing PPE   -> yellow light + buzzer
unknown face               -> red light + buzzer
no face                    -> all lights off
```

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

Then run either lab:

```bash
python lab1.py
python lab2.py
```

When a lab starts, it opens a camera preview tab:

```text
http://127.0.0.1:8080
```

If the Raspberry Pi has no desktop browser, open this from another device on the same network:

```text
http://<raspberry-pi-ip>:8080
```
