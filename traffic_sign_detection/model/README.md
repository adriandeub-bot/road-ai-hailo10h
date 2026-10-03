\# Traffic Sign Detection Model



This directory is reserved for the trained traffic-sign detection model used by this module.



\## Required Model



The detection scripts expect the following file:



```text

traffic\_detector.pt

```



However, the current project scripts reference the model as:



```text

traffic\_sign\_detector.pt

```



Therefore, the expected file name for the current implementation is:



```text

traffic\_sign\_detection/model/traffic\_sign\_detector.pt

```



\## Model Information



\- Architecture: \*\*YOLO11n\*\*

\- Task: Object Detection

\- Number of classes: \*\*15\*\*

\- Training epochs: \*\*50\*\*

\- Batch size: \*\*16\*\*

\- Parameters: approximately \*\*2.59 million\*\*

\- GFLOPs: approximately \*\*6.46\*\*



\## Classes



The trained model contains the following classes:



```text

0  Green Light

1  Red Light

2  Speed Limit 10

3  Speed Limit 100

4  Speed Limit 110

5  Speed Limit 120

6  Speed Limit 20

7  Speed Limit 30

8  Speed Limit 40

9  Speed Limit 50

10 Speed Limit 60

11 Speed Limit 70

12 Speed Limit 80

13 Speed Limit 90

14 Stop

```



\## Model Availability



The model binary is intentionally excluded from Git version control.



The repository `.gitignore` excludes PyTorch model files such as:



```text

\*.pt

\*.pth

```



This keeps large binary model files outside the source repository.



To use the traffic-sign detection scripts, place the trained model at:



```text

traffic\_sign\_detection/model/traffic\_sign\_detector.pt

```



\## Exported Formats



The original project also contains exported versions of the model, including:



\- ONNX

\- NCNN



These exported model files are also excluded from the repository.



Future versions of this project may include a Hailo-compatible model specifically optimized for the \*\*Hailo-10H\*\* accelerator.

