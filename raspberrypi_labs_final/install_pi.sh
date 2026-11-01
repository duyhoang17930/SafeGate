#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y python3-venv python3-pip python3-opencv python3-gpiozero python3-lgpio i2c-tools

python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ppe.txt

echo "Install complete. Activate with: source .venv/bin/activate"
