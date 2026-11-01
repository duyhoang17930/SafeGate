# Atharion PPE detection dataset — v1.0-public

Construction-site personal protective equipment, as YOLO detection labels.
Assembled for the Samsung Innovation Campus capstone of Atharion (Group 17)
from public sources whose licences permit redistribution.

## Contents

- **1,130 images**, train 791, valid 170, test 169.
- **5,355 boxes** over 3 classes: `Person` 2,002, `Hardhat` 1,776, `Safety Vest` 1,577.
- YOLO format: one `.txt` per image, `class cx cy w h`, normalised.
- Splits are assigned by **scene group**, not by file: near-duplicates and
  frames from one video stay on the same side, so the validation score is not
  inflated by having already seen the frame next door.

## Sources and licences

| source | images | licence |
|---|---:|---|
| [Construction-PPE 1.0.0](https://docs.ultralytics.com/datasets/detect/construction-ppe/) (Ultralytics) | 1,026 | AGPL-3.0 |
| [Construction Site Safety](https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety) v28 | 104 | CC BY 4.0 |

Per-file attribution is in `attribution.csv`; obligations are in `NOTICE.md`.
Labels were regenerated from a documented class mapping. No annotation was
invented, and no image was edited.

## The larger version, and why it is not here

The training set used internally is larger. The difference is one source with
no licence file, which we may train on but may not redistribute. Rather than
guess at permission, it is excluded. `tools/fetch_sources.py` pins every
source archive by SHA-256, so the full set is reproducible from the originals.

## Known limitations — read before you trust an evaluation

- **Domain gap.** These are largely staged and photographic construction
  images, not fixed-camera site CCTV. Only 5.7% of objects are
  "small" (under 32 px at 640×640), whereas on real overhead site cameras most
  workers are small. Expect a drop when deploying to CCTV.
- **Positive-only taxonomy.** There is no `NO-Hardhat` class. Non-compliance is
  meant to be derived geometrically — a detected worker with no hardhat
  associated to their head region — not detected directly. A missing class is
  not evidence of a bare head.
- **No compliance ground truth.** The fraction of workers here without an
  associated vest is an annotation-coverage artefact, not a violation rate. Do
  not use this dataset to estimate how often real workers are non-compliant.
- **Source imbalance.** 91% of images come from one source, so its
  photographic conventions dominate.
- **Person boxes vary in convention.** Some sources box the full body, others
  crop at the waist under occlusion. This measurably shifts where a vest sits
  inside the box — see the measured geometry below.
- **Upstream augmentation was removed, not kept.** One source ships a Roboflow
  export whose training split is augmented by mosaic — four unrelated photos
  stitched into one frame with their labels merged. Those derivatives are
  excluded here: they are not site imagery, and because every mosaic draws
  tiles from the same pool, two of them can share a tile while remaining
  different images, which defeats duplicate detection based on image hashing.

## Measured association geometry

If you are building compliance logic on top of this, these are measured on the
826 single-worker images where PPE-to-worker assignment is unambiguous:

| item | position inside the worker box (p5 / median / p95) |
|---|---|
| Hardhat centre | 0.05 / 0.11 / 0.30 |
| Safety Vest centre | 0.30 / 0.41 / 0.69 |

0.0 is the top of the worker box and 1.0 the bottom. A vest sits far lower than
a naive `[0.15, 0.55]` torso band assumes; measure before you hard-code a zone.

## Citation

Cite the upstream sources listed above. This release is a re-packaging: it
contributes the consolidation, the leakage-free splits and the verification,
not the photographs.

