# Enriched PPE model training report

## Artifacts

- `models/ppe_best.pt`: fine-tuned YOLO11n checkpoint.
- `models/ppe_best.onnx`: fixed 320x320 ONNX export used by the pipeline.
- The ONNX file was synchronized to `raspberrypi_labs_final/models/ppe_best.onnx` and `raspberrypi_face_access/models/ppe_best.onnx`.
- Reproducible Kaggle notebook: `notebooks/ppe-yolo-enriched-training.ipynb`.

The model was fine-tuned from the previous `ppe_best.pt` on `datasets/ppe_enriched/data.yaml`. The run used 60 epochs, 640px training images, batch size 16, and a Kaggle Tesla T4. Training completed in about 1.32 hours. The dataset contains 8,396 train, 275 validation, and 171 test images.

## Held-out test results

Kaggle validation at 640px reported overall precision 0.902, recall 0.824, mAP50 0.880, and mAP50-95 0.523. Vest AP50 was 0.923 and vest AP50-95 was 0.586.

I also compared the old and enriched ONNX models on the same 171-image test split at 320px using CPU ONNX Runtime:

| Metric | Previous ONNX | Enriched ONNX |
| --- | ---: | ---: |
| Precision | 0.715 | 0.866 |
| Recall | 0.392 | 0.798 |
| mAP50 | 0.490 | 0.850 |
| mAP50-95 | 0.223 | 0.483 |
| Vest AP50 | 0.407 | 0.906 |
| Vest AP50-95 | 0.187 | 0.547 |

These scores describe this dataset split; validate with footage from the intended camera before relying on access or safety decisions.

## Provenance

The enriched dataset combines the project's prior PPE dataset with Atharion PPE detection dataset v1.0-public. Keep `datasets/ppe_enriched/NOTICE.md` and `datasets/ppe_enriched/attribution-atharion.csv` with the data. See the [Atharion release](https://github.com/atharion-team/ppe-dataset-v1/releases/tag/v1.0) for its source and mixed license details.
