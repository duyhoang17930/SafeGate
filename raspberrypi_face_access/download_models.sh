#!/usr/bin/env bash
set -euo pipefail

mkdir -p models

wget -O models/face_detection_yunet.onnx \
  https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_detection_yunet/face_detection_yunet_2026may.onnx

wget -O models/face_recognition_sface.onnx \
  https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx

echo "Face models downloaded into models/"

