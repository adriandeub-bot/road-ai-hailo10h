\# Traffic Sign Detection



Traffic sign detection module based on \*\*YOLO11n\*\*, trained for detecting traffic signs and traffic lights in road scenes.



This module is part of the `road-ai-hailo10h` project and is intended to provide traffic-sign detection capabilities for road-analysis applications on Raspberry Pi and Hailo hardware.



\## Model



The original detector was trained using \*\*Ultralytics YOLO11n\*\* and fine-tuned for 50 epochs with a batch size of 16.



The trained model is intentionally \*\*not included in this repository\*\* because model binaries and exported weights are excluded from version control.



Expected model path:



```text

traffic\_sign\_detection/model/traffic\_sign\_detector.pt

```



See \[`model/README.md`](./model/README.md) for information about obtaining and deploying the model.



\## Detected Classes



The trained model contains 15 classes:



| ID | Class |

|---:|---|

| 0 | Green Light |

| 1 | Red Light |

| 2 | Speed Limit 10 |

| 3 | Speed Limit 100 |

| 4 | Speed Limit 110 |

| 5 | Speed Limit 120 |

| 6 | Speed Limit 20 |

| 7 | Speed Limit 30 |

| 8 | Speed Limit 40 |

| 9 | Speed Limit 50 |

| 10 | Speed Limit 60 |

| 11 | Speed Limit 70 |

| 12 | Speed Limit 80 |

| 13 | Speed Limit 90 |

| 14 | Stop |



> The class mapping above corresponds to the actual trained model and is therefore considered the authoritative class definition for this project.



\## Example Images



The repository includes a small set of example images for testing and documentation:



```text

examples/images/

├── green\_light.jpg

├── red\_light.jpg

├── speed\_limit\_40.jpg

├── speed\_limit\_50.jpg

└── stop\_sign.jpg

```



The complete training dataset is not included in this repository.



\## Image Detection



The `process\_image.py` script loads the trained model, processes an input image, and displays detected traffic signs with bounding boxes and class names.



Default input:



```text

data/input/stop\_sign.jpg

```



Run:



```bash

python process\_image.py

```



The script expects the model at:



```text

./model/traffic\_sign\_detector.pt

```



\## Video Detection



The `process\_video.py` script processes a video frame by frame and displays detected traffic signs using bounding boxes.



Default input:



```text

data/input/traffic\_signs.mp4

```



Run:



```bash

python process\_video.py

```



Press `q` to stop the visualization.



\## Original Training Results



The original training run reported the following validation metrics:



\- Precision: \*\*0.95049\*\*

\- Recall: \*\*0.90534\*\*

\- mAP@50: \*\*0.95912\*\*

\- mAP@50-95: \*\*0.83597\*\*

\- Parameters: approximately \*\*2.59 million\*\*

\- GFLOPs: approximately \*\*6.46\*\*



These values correspond to the original validation run and should not be interpreted as current performance on new datasets or road conditions.



\## Dataset



The original model was trained using the \*\*Self-Driving Cars Dataset\*\* from Roboflow.



Dataset:



https://universe.roboflow.com/selfdriving-car-qtywx/self-driving-cars-lfjou/dataset/6



The original dataset contained:



\- 4,969 images

\- 3,530 training images

\- 801 validation images

\- 638 test images

\- Image dimension: 416 × 416



\## Limitations



The original implementation was primarily designed for image-based detection.



For real-time road analysis, additional optimization may be required, including:



\- model conversion to a hardware-accelerated format;

\- inference optimization;

\- video pipeline optimization;

\- frame-rate management;

\- tracking and temporal filtering;

\- testing under different lighting and weather conditions.



The current Python scripts use the Ultralytics runtime and are not yet integrated directly with the Hailo-10H inference pipeline.



\## Project Status



Current module contents:



\- YOLO11n traffic-sign detection scripts

\- Example traffic-sign images

\- Model documentation

\- Original validation metrics



Future work may include:



\- Hailo-10H model conversion;

\- real-time inference;

\- traffic-sign tracking;

\- integration with vehicle detection;

\- integration with lane detection;

\- unified road-scene analysis.

