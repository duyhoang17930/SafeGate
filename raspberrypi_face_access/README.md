# Raspberry Pi Face Access

This folder is the Raspberry Pi deploy package.

It uses the cloned `FaceAccess` idea with OpenCV YuNet + SFace for face access:

- known face: show granted on LCD/display, turn servo to 90 degrees, then lock again
- unknown face: show denied on LCD/display, turn on buzzer
- no face: wait silently

Your trained PPE model is included as:

```text
models/ppe_best.onnx
```

Face access does not require the PPE model. Set `ENABLE_PPE_STATUS = True` in `config.py` only if you want to also display helmet/vest status.

## Hardware Pins

Default BCM pins:

```text
green LED: GPIO17
red LED:   GPIO27
servo:     GPIO18
buzzer:    GPIO22
LCD I2C:   address 0x27
```

Edit `config.py` if your wiring is different.

## Install On Raspberry Pi

```bash
cd raspberrypi_face_access
bash install_pi.sh
source .venv/bin/activate
bash download_models.sh
```

If you already installed OpenCV another way, keep `opencv-contrib-python` out of the venv and use the system package.

`install_pi.sh` installs `python3-opencv` through apt and creates the venv with `--system-site-packages`, which is usually the least painful path on Raspberry Pi.

## Register A User

Stand in front of the camera:

```bash
python register_user.py --student-id 001 --name Huy
```

Register each allowed person once.

## Run Always-On Access

```bash
python access_loop.py
```

For boot startup, create a `systemd` service that runs:

```bash
/path/to/raspberrypi_face_access/.venv/bin/python /path/to/raspberrypi_face_access/access_loop.py
```

## Notes

- The face model files are not bundled. Run `download_models.sh` on the Pi.
- `users.db` is created automatically.
- Access logs are written to `logs/access.csv`.
- If your LCD is not connected, the code falls back to console output.

To enable optional PPE display status:

```bash
pip install -r requirements-ppe.txt
```

Then set this in `config.py`:

```python
ENABLE_PPE_STATUS = True
```
