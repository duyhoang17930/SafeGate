# Enriched PPE dataset

This is a separate combined dataset. The original `datasets/ppe` remains unchanged.

It combines the current project PPE dataset with Atharion PPE detection dataset v1.0-public. The Atharion release contributes 1,130 images and 1,577 Safety Vest boxes, alongside Person and Hardhat labels. Source class IDs were remapped from `Person, Hardhat, Safety Vest` to this project order `person, helmet, vest`.

Atharion splits were preserved: 791 train, 170 validation, 169 test. Files are prefixed `atharion__`; the per-image source records are in `attribution-atharion.csv`. The original license notice and dataset card are included here.

Combined split sizes are 8,396 train, 275 validation, and 171 test images. The training set has 8,947 vest boxes, up from 7,882 in the original set (1,065 additional training vest boxes). The Atharion test and validation splits add 220 and 292 vest boxes, respectively.

The added release contains positive labels for Person, Hardhat, and Safety Vest; it has no `NoVest` class. The source card also notes a domain gap from fixed-camera site footage and that 91% of its images come from one source, so evaluate on footage from the intended camera before relying on the result.

The added images have mixed AGPL-3.0 and CC BY 4.0 provenance. Keep `NOTICE.md` and `attribution-atharion.csv` with this data; see the source [release](https://github.com/atharion-team/ppe-dataset-v1/releases/tag/v1.0) and its [dataset card](https://github.com/atharion-team/ppe-dataset-v1/blob/main/DATASET_CARD.md).

Archive SHA-256: `f5f6f1966c4bdfff4151ee68fa0da21f446e1b788d15280e5f70028c69ec88c5`

Train with:

```bash
python tools/train_ppe.py --model yolo11n.pt --data datasets/ppe_enriched/data.yaml --output models/ppe_enriched_best.pt
```
