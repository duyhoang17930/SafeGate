\## Recommended models, libraries, and official references



Use maintained and lightweight libraries suitable for Raspberry Pi CPU deployment.



\### 1. PPE / person detection model



Use Ultralytics YOLO nano as the base detector.



Preferred starting models:



\- YOLO11n

\- alternatively YOLOv8n if compatibility with an older project is required



Official YOLO11 documentation:

https://docs.ultralytics.com/models/yolo11/



Ultralytics repository:

https://github.com/ultralytics/ultralytics



Installation:



```bash

pip install ultralytics

```



The pretrained generic YOLO model can detect `person`, but it does NOT natively provide the custom PPE classes required by this project.



Therefore create/fine-tune a custom detector for:



\- person

\- helmet

\- vest



Use a pretrained nano checkpoint as initialization.



Example:



```python

from ultralytics import YOLO



model = YOLO("yolo11n.pt")



model.train(

&#x20;   data="ppe.yaml",

&#x20;   epochs=80,

&#x20;   imgsz=640,

&#x20;   batch=16,

&#x20;   device=0

)

```



After training, the expected checkpoint is:



```text

runs/detect/train/weights/best.pt

```



Copy it to:



```text

models/ppe\_best.pt

```



\### Example PPE datasets / projects



The following repositories can be used as references for dataset structure, PPE classes, training code and inference implementation:



VoxDroid PPE Detection:

https://github.com/VoxDroid/Construction-Site-Safety-PPE-Detection



SiteWatch:

https://github.com/AitchEm-bot/sitewatch



PPE Detection for Construction Site Safety:

https://github.com/zEuS0390/ppe-detection-for-construction-site-safety



HazardLens:

https://github.com/Smear6uard/HazardLens



Do not blindly copy their architecture.



Use them mainly to understand:



\- dataset labeling

\- PPE classes

\- YOLO training

\- construction-site examples

\- alert logic



For this project, keep the model intentionally small.



\### 2. Example YOLO dataset structure



Create:



```text

datasets/ppe/

├── images/

│   ├── train/

│   ├── val/

│   └── test/

└── labels/

&#x20;   ├── train/

&#x20;   ├── val/

&#x20;   └── test/

```



Create:



```text

ppe.yaml

```



Example:



```yaml

path: datasets/ppe



train: images/train

val: images/val

test: images/test



names:

&#x20; 0: person

&#x20; 1: helmet

&#x20; 2: vest

```



Labels must use YOLO format:



```text

class\_id x\_center y\_center width height

```



with normalized coordinates.



\### 3. Training PPE model



Training should normally happen on:



\- desktop PC with NVIDIA GPU

\- laptop GPU

\- Google Colab



Do NOT train the main YOLO model on Raspberry Pi unless only performing a tiny experiment.



Example training command:



```bash

yolo detect train \\

&#x20;   model=yolo11n.pt \\

&#x20;   data=ppe.yaml \\

&#x20;   epochs=80 \\

&#x20;   imgsz=640 \\

&#x20;   batch=16

```



Python equivalent:



```python

from ultralytics import YOLO



model = YOLO("yolo11n.pt")



model.train(

&#x20;   data="ppe.yaml",

&#x20;   epochs=80,

&#x20;   imgsz=640,

&#x20;   batch=16,

&#x20;   patience=20,

&#x20;   workers=4

)

```



During training evaluate:



\- precision

\- recall

\- mAP50

\- mAP50-95

\- confusion matrix



Do not choose a checkpoint based only on training loss.



Use the best validation checkpoint:



```text

best.pt

```



\### 4. Export trained YOLO model to ONNX



Important:



The model is first trained as a PyTorch checkpoint.



The correct pipeline is:



```text

yolo11n.pt

&#x20;  ↓

train PPE dataset

&#x20;  ↓

best.pt

&#x20;  ↓

export

&#x20;  ↓

best.onnx

```



Official Ultralytics export documentation:



https://docs.ultralytics.com/modes/export/



Create:



```text

tools/export\_ppe\_onnx.py

```



Example implementation:



```python

from ultralytics import YOLO



MODEL\_PATH = "models/ppe\_best.pt"



model = YOLO(MODEL\_PATH)



model.export(

&#x20;   format="onnx",

&#x20;   imgsz=320,

&#x20;   simplify=True,

&#x20;   dynamic=False

)

```



The expected result should be similar to:



```text

models/ppe\_best.onnx

```



Also provide a CLI option:



```bash

yolo export \\

&#x20;   model=models/ppe\_best.pt \\

&#x20;   format=onnx \\

&#x20;   imgsz=320 \\

&#x20;   simplify=True

```



Use fixed input size on Raspberry Pi unless dynamic shapes are genuinely required.



Recommended initial Raspberry Pi inference size:



```text

320x320

```



If accuracy is insufficient, test:



```text

416x416

```



or:



```text

640x640

```



Measure actual FPS before deciding.



\### 5. Test the ONNX PPE model



Use ONNX Runtime for CPU inference.



Official ONNX Runtime project:



https://github.com/microsoft/onnxruntime



Install:



```bash

pip install onnxruntime

```



Create:



```text

tools/test\_ppe\_onnx.py

```



It should:



1\. load `models/ppe\_best.onnx`

2\. read an image

3\. preprocess it

4\. run ONNX Runtime inference

5\. perform post-processing/NMS if required

6\. display bounding boxes

7\. print inference time



Prefer using the Ultralytics wrapper when possible because it handles model metadata and post-processing:



```python

from ultralytics import YOLO



model = YOLO("models/ppe\_best.onnx")

results = model("test.jpg")

```



But also keep the detector architecture separated so direct ONNX Runtime inference can be implemented later if performance optimization is required.



\### 6. Raspberry Pi deployment format



Support ONNX first because it is easy to debug and portable.



Also support NCNN as an optional Raspberry Pi optimization.



Official Raspberry Pi deployment documentation:



https://docs.ultralytics.com/guides/raspberry-pi/



Export NCNN:



```python

from ultralytics import YOLO



model = YOLO("models/ppe\_best.pt")



model.export(

&#x20;   format="ncnn",

&#x20;   imgsz=320

)

```



Expected output:



```text

models/ppe\_best\_ncnn\_model/

```



Architecture must allow switching between:



```text

models/ppe\_best.pt

models/ppe\_best.onnx

models/ppe\_best\_ncnn\_model/

```



through `config.py`.



\### 7. Face detection



Use a lightweight face detector.



Preferred options:



\#### Option A — InsightFace detection



Use InsightFace FaceAnalysis.



Official repository:



https://github.com/deepinsight/insightface



Install:



```bash

pip install insightface onnxruntime

```



InsightFace provides:



\- face detection

\- face alignment

\- face embeddings

\- face recognition



Use CPU execution on Raspberry Pi.



\#### Option B — OpenCV YuNet



YuNet is an alternative lightweight face detector.



Official OpenCV Zoo model:



https://github.com/opencv/opencv\_zoo/tree/main/models/face\_detection\_yunet



YuNet can be useful if InsightFace detection is too heavy.



The implementation should make FaceDetector replaceable.



For example:



```python

class FaceDetector:

&#x20;   def detect(self, image):

&#x20;       ...

```



Do not tightly couple face detection with the rest of the application.



\### 8. Face recognition model



Use InsightFace / ArcFace-style embeddings.



Official InsightFace repository:



https://github.com/deepinsight/insightface



InsightFace supports ONNX models for face analysis.



Use:



```python

from insightface.app import FaceAnalysis

```



Example:



```python

from insightface.app import FaceAnalysis



app = FaceAnalysis(

&#x20;   name="buffalo\_l",

&#x20;   providers=\["CPUExecutionProvider"]

)



app.prepare(

&#x20;   ctx\_id=-1,

&#x20;   det\_size=(320, 320)

)

```



However, Raspberry Pi performance is more important than maximum recognition accuracy.



Therefore structure the project so a smaller InsightFace model package or lightweight face recognition ONNX model can later replace the default model.



Do not assume `buffalo\_l` is the final Raspberry Pi choice.



Provide configuration:



```python

FACE\_MODEL\_NAME = "buffalo\_l"

FACE\_DETECTION\_SIZE = (320, 320)

```



\### Important model licensing note



InsightFace library code can be used under its software license, but pretrained model licensing can differ.



Do not silently bundle pretrained InsightFace weights into the project.



Document the source and license of every pretrained model used.



For a school/demo prototype, downloading the officially provided research model may be acceptable depending on the project's usage.



For commercial deployment, require checking/replacing models with appropriately licensed weights.



\### 9. Face database — do not retrain ArcFace for every new person



Do NOT train a new face recognition neural network just to add a new person.



The intended workflow is:



```text

photo of Huy

&#x20;   ↓

face detection

&#x20;   ↓

face alignment

&#x20;   ↓

ArcFace

&#x20;   ↓

embedding vector

&#x20;   ↓

store vector

```



Repeat this for each known person.



Example database:



```text

face\_db/

├── Huy/

│   ├── front.jpg

│   ├── left.jpg

│   ├── right.jpg

│   ├── indoor.jpg

│   └── outdoor.jpg

│

└── Nam/

&#x20;   ├── front.jpg

&#x20;   ├── left.jpg

&#x20;   └── right.jpg

```



Generate embeddings from every valid image.



Normalize embeddings:



```python

embedding = embedding / np.linalg.norm(embedding)

```



Average embeddings belonging to the same person:



```python

person\_embedding = np.mean(embeddings, axis=0)

person\_embedding /= np.linalg.norm(person\_embedding)

```



Store:



```text

data/faces.pkl

```



or optionally:



```text

data/faces.npz

```



\### 10. Face matching



For an incoming camera face:



```text

camera face

&#x20;  ↓

face detector

&#x20;  ↓

alignment

&#x20;  ↓

ArcFace embedding

&#x20;  ↓

L2 normalize

&#x20;  ↓

cosine similarity

&#x20;  ↓

compare against database

```



Example:



```python

similarity = np.dot(query\_embedding, stored\_embedding)

```



because both vectors are L2 normalized.



Find:



```python

best\_name

best\_similarity

```



If:



```python

best\_similarity < FACE\_SIMILARITY\_THRESHOLD

```



return:



```text

Unknown

```



Do NOT blindly hard-code a threshold copied from an internet example.



Provide:



```python

FACE\_SIMILARITY\_THRESHOLD = 0.45

```



only as an initial tuning value.



Create a calibration script:



```text

tools/calibrate\_face\_threshold.py

```



The script should compare:



\- same-person image pairs

\- different-person image pairs



and print similarity distributions so an appropriate threshold can be selected for the actual camera and environment.



\### 11. Recommended libraries



Use approximately:



```text

Python

OpenCV

NumPy

Ultralytics

ONNX Runtime

InsightFace

```



Suggested `requirements.txt`:



```txt

numpy

opencv-python

ultralytics

onnxruntime

insightface

```



On Raspberry Pi, if regular OpenCV installation causes issues, document Raspberry Pi-specific installation alternatives instead of silently installing large unnecessary packages.



\### 12. Complete AI pipeline



Implement this architecture:



```text

Raspberry Pi Camera / USB Camera

&#x20;             |

&#x20;             v

&#x20;       OpenCV capture

&#x20;             |

&#x20;             v

&#x20;       PPE detector

&#x20;     YOLO nano model

&#x20;             |

&#x20;   +---------+---------+

&#x20;   |                   |

&#x20;   v                   v

&#x20;Person bbox       helmet / vest

&#x20;   |

&#x20;   v

&#x20;Person tracker

&#x20;   |

&#x20;   v

&#x20;Crop person ROI

&#x20;   |

&#x20;   v

&#x20;Face detector

&#x20;   |

&#x20;   v

&#x20;Face alignment

&#x20;   |

&#x20;   v

&#x20;Face embedding

&#x20;  ArcFace

&#x20;   |

&#x20;   v

&#x20;cosine similarity

&#x20;   |

&#x20;   v

&#x20;Huy / Nam / Unknown

&#x20;   |

&#x20;   +----------------------+

&#x20;                          |

&#x20;                          v

&#x20;                   PPE association

&#x20;                          |

&#x20;                          v

&#x20;              Huy

&#x20;              Helmet: MISSING

&#x20;              Vest: OK

&#x20;                          |

&#x20;                          v

&#x20;                   violation logger

```



\### 13. Recommended development workflow



Do not integrate everything immediately.



\#### Step 1 — Camera only



Run:



```bash

python tools/test\_camera.py

```



Confirm camera output is stable.



\#### Step 2 — Test pretrained YOLO person detection



Before custom PPE training, test:



```python

from ultralytics import YOLO



model = YOLO("yolo11n.pt")

model.predict(source=0)

```



Confirm the Pi/camera pipeline works.



\#### Step 3 — Train custom PPE model on PC



Train:



```text

person

helmet

vest

```



Get:



```text

best.pt

```



\#### Step 4 — Test `best.pt` on PC



Use test images/videos.



Check actual PPE matching.



\#### Step 5 — Export `best.pt` to ONNX



Generate:



```text

best.onnx

```



\#### Step 6 — Compare `.pt` and `.onnx`



Verify:



\- detections are similar

\- class indices are correct

\- confidence scores are reasonable



\#### Step 7 — Build face database



Add 5-10 photos for each known person.



Run:



```bash

python tools/build\_face\_database.py

```



\#### Step 8 — Test face recognition separately



Run:



```bash

python tools/test\_face\_recognition.py

```



Display:



```text

Predicted: Huy

Similarity: 0.71

```



\#### Step 9 — Add tracking



Associate:



```text

track\_id → person\_name

```



Reuse identity across frames.



\#### Step 10 — Combine PPE + identity



Expected output:



```text

ID 4 | Huy

Helmet: OK

Vest: MISSING

```



\#### Step 11 — Optimize Raspberry Pi



Try:



```text

640x480 camera

320x320 YOLO inference

PPE every 2 frames

face recognition every 10 frames

tracking every frame

```



Measure:



```text

camera FPS

AI FPS

YOLO inference ms

face inference ms

CPU usage

RAM usage

temperature

```



\#### Step 12 — Try NCNN



Once ONNX version works correctly, export YOLO to NCNN and benchmark it against ONNX.



Do not optimize before the basic pipeline is correct.



\### 14. Benchmark tool



Create:



```text

tools/benchmark.py

```



It must report:



```text

Model: models/ppe\_best.onnx

Resolution: 320

Frames: 300



Average YOLO inference: XX ms

Average face recognition: XX ms

Pipeline FPS: XX

CPU usage: XX %

RAM: XX MB

```



Allow comparing:



```text

PT

ONNX

NCNN

```



Do not claim one backend is faster without measuring it on the actual Raspberry Pi.

