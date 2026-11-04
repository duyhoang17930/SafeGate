# Run the PPE model on a Windows laptop

This folder contains a copy of the project's PPE detector, twelve sample photos, and a script for running inference on your own photos or webcam. The model runs locally on the laptop CPU after setup.

## First-time setup

1. Install Python 3.10 or newer and enable the Python launcher (`py`) during installation.
2. Double-click `setup_windows.bat`. It creates a private `.venv` in this folder and installs the packages. Internet access is needed for this install; rerun it after requirements change.
3. Double-click `run_model.bat` to open your webcam. To run the bundled sample photos instead, use `run_model.bat --source test_images`. Annotated copies are saved under `results`.

## Try your webcam or your own photo

The webcam window shows live detections and whether a helmet and vest were detected. The Command Prompt prints the same status once per second. Press **Q** in the video window to stop. To choose a different camera, replace `0` with its index.

Open Command Prompt in this folder to run:

```bat
run_model.bat --source 0
run_model.bat --source test_images
run_model.bat --source "C:\path\to\your\photo.jpg"
```

You can also provide a folder of images with `--source "C:\path\to\photos"`.

The sample photos cover these cases: helmet and vest present, helmet missing, vest missing, and both missing. The detector reports person, helmet, and vest boxes; compare its detections with the sample names. A missing detection means the model did not detect that item in the current frame. Results depend on image quality and camera angle.

## Files

- `models/ppe_best.onnx` - the trained model copied from the main project.
- `test_images/` - sample photos for a quick check.
- `test_ppe.py` - inference script for photos, folders, and cameras.
- `results/` - created automatically when image inference runs.
