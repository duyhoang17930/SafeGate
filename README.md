# PPE + Face Recognition Safety Pipeline

This project implements the phases from `prompt.md` for a Raspberry Pi-friendly prototype:

1. Camera smoke test
2. YOLO PPE training for `person`, `helmet`, and `vest`
3. PT to ONNX export
4. ONNX/NCNN-compatible PPE inference
5. InsightFace face embeddings
6. Face database build and threshold calibration
7. New face registration without retraining ArcFace
8. Tracking, PPE association, identity reuse, violation logging
9. Benchmarking PT/ONNX/NCNN on the actual target device

## Current PPE Model

The default `models/ppe_best.pt` and 320x320 `models/ppe_best.onnx` are the enriched YOLO11n model. The ONNX deployment copies in both Raspberry Pi packages were updated to match. Training details and held-out results are in [models/PPE_TRAINING_REPORT.md](models/PPE_TRAINING_REPORT.md); the saved Kaggle notebook is [notebooks/ppe-yolo-enriched-training.ipynb](notebooks/ppe-yolo-enriched-training.ipynb).

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On Raspberry Pi, OpenCV wheels can be heavy. If `opencv-python` is not suitable for your OS image, install the distro OpenCV package or a lighter wheel, then keep the Python imports the same.

## PPE Dataset

Place YOLO-format data under:

```text
datasets/ppe/images/train
datasets/ppe/images/val
datasets/ppe/images/test
datasets/ppe/labels/train
datasets/ppe/labels/val
datasets/ppe/labels/test
```

Classes are configured in `ppe.yaml`:

```text
0 person
1 helmet
2 vest
```

Download a Roboflow PPE dataset with an API key:

```bash
set ROBOFLOW_API_KEY=your_key_here
python tools/download_roboflow_ppe.py --clear-output
```

This downloads `qsf-eisng/construction-ppe-part-1` version 1 and remaps:

```text
person -> person
worker -> person
helmet -> helmet
vest   -> vest
reflectiveVest -> vest
all other classes -> ignored
```

The downloader defaults to `v2-wo7jr/ppe-construction-detection-dataset-utu1c` version 12 because the public `qsf-eisng/construction-ppe-part-1` downloadable version currently exports only two images.

To try the smaller public export anyway:

```bash
python tools/download_roboflow_ppe.py --workspace qsf-eisng --project construction-ppe-part-1 --version 1 --clear-output
```

## Phase Commands

Camera test:

```bash
python tools/test_camera.py
```

Train PPE model on a GPU machine:

```bash
python tools/train_ppe.py --model yolo11n.pt --data ppe.yaml --epochs 80 --imgsz 640 --batch 16
```

Export ONNX:

```bash
python tools/export_ppe_onnx.py --model models/ppe_best.pt --imgsz 320
```

Export NCNN:

```bash
python tools/export_ppe_ncnn.py --model models/ppe_best.pt --imgsz 320
```

Test PPE model:

```bash
python tools/test_ppe_onnx.py --model models/ppe_best.onnx --source test.jpg
```

Smoke-test pretrained YOLO person detection before custom training:

```bash
python tools/test_yolo_person.py --source 0
```

Compare `best.pt` and exported ONNX on the same image:

```bash
python tools/compare_ppe_models.py test.jpg --a models/ppe_best.pt --b models/ppe_best.onnx
```

Build face database from `face_db/<person>/*.jpg`:

```bash
python tools/build_face_database.py
```

Register a new face from existing images:

```bash
python tools/register_face.py Huy --images face_db/Huy
```

Register a new face by camera capture:

```bash
python tools/register_face.py Huy --capture --samples 8
```

Test face recognition:

```bash
python tools/test_face_recognition.py test_face.jpg
```

Calibrate face threshold:

```bash
python tools/calibrate_face_threshold.py
```

Run full pipeline:

```bash
python tools/run_pipeline.py
```

Benchmark target hardware:

```bash
python tools/benchmark.py --model models/ppe_best.onnx --frames 300 --imgsz 320
```

## Face Registration Feature

`tools/register_face.py` adds a person by extracting normalized ArcFace embeddings from images and updating `data/faces.pkl`. It does not train a new neural network.

Use 5-10 clear photos per person. Avoid photos with multiple faces because those samples are skipped.

## Model Licensing

This repo includes the project-fine-tuned PPE checkpoint and ONNX export. The upstream `yolo11n.pt` initialization checkpoint is not included. PPE training data provenance and its mixed source licenses are documented in `datasets/ppe_enriched/NOTICE.md`; keep that notice and `attribution-atharion.csv` with the dataset. Record the source and license for all face-recognition weights before using them beyond school/demo work.
