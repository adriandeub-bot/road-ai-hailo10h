\# Road AI — Raspberry Pi 5 + Hailo-10H



Sistema de Edge AI desarrollado sobre Raspberry Pi 5 y acelerado mediante Hailo-10H para el análisis de escenas de carretera.



El proyecto integra diferentes modelos de visión artificial para detectar y analizar elementos presentes en una escena vial:



\- 🚗 Vehículos

\- 🚦 Señales de tráfico

\- 🛣️ Carriles



El objetivo es ejecutar inferencia de inteligencia artificial localmente en el Raspberry Pi 5, utilizando el acelerador Hailo-10H para obtener un procesamiento eficiente en el borde (Edge AI).



\---



\## 🚀 Características



\### 🚗 Detección de vehículos



Detección y seguimiento de vehículos utilizando modelos YOLO ejecutados mediante el acelerador Hailo-10H.



Características:



\- Detección de vehículos.

\- Identificación mediante bounding boxes.

\- Tracking de objetos.

\- Asignación de IDs a objetos detectados.

\- Procesamiento de video.



\### 🚦 Detección de señales de tráfico



Sistema basado en YOLO11 para detectar señales de tráfico en imágenes y videos.



Características:



\- Inferencia sobre imágenes.

\- Inferencia sobre videos.

\- Bounding boxes.

\- Clasificación de señales.

\- Modelo personalizado entrenado para señales de tráfico.



\### 🛣️ Detección de carriles



Sistema de detección de carriles basado en UFLD v2 ejecutado mediante Hailo-10H.



Características:



\- Detección de líneas de carril.

\- Procesamiento de video.

\- Preprocesamiento específico para el modelo.

\- Visualización de los carriles detectados.



\---



\## 🧠 Arquitectura



La arquitectura general del proyecto está compuesta por tres módulos principales:



```text



&#x20;                          ┌───────────────────┐

&#x20;                        │    Input Video    │

&#x20;                        └─────────┬─────────┘

&#x20;                                  │

&#x20;                                  ▼

&#x20;                      ┌───────────────────────┐

&#x20;                      │     Road AI System    │

&#x20;                      └───────────┬───────────┘

&#x20;                                  │

&#x20;             ┌────────────────────┼────────────────────┐

&#x20;             │                    │                    │

&#x20;             ▼                    ▼                    ▼

&#x20;      ┌─────────────┐      ┌──────────────┐     ┌─────────────┐

&#x20;      │  Vehicles   │      │ Traffic Signs│     │    Lanes    │

&#x20;      │    YOLO     │      │    YOLO11    │     │   UFLD v2   │

&#x20;      └──────┬──────┘      └──────┬───────┘     └──────┬──────┘

&#x20;             │                    │                    │

&#x20;             └────────────────────┼────────────────────┘

&#x20;                                  │

&#x20;                                  ▼

&#x20;                        ┌───────────────────┐

&#x20;                        │ Annotated Output  │

&#x20;                        └───────────────────┘


🖥️ Hardware
El sistema fue desarrollado utilizando:

| Componente | Especificación |
|---|---|
| SBC | Raspberry Pi 5 |
| AI Accelerator | Raspberry Pi AI HAT+ 2 |
| AI Processor | Hailo-10H |
| AI Performance | 40 TOPS |
| Interface | PCIe |
| Operating System | Raspberry Pi OS 64-bit |
| Architecture | ARM64 |


🤖 AI Models
El proyecto utiliza diferentes modelos según la tarea:
Tarea	Modelo	Aceleración
Vehicle Detection	YOLOv8m	Hailo-10H
Traffic Sign Detection	YOLO11	CPU / exportaciones disponibles
Lane Detection	UFLD v2	Hailo-10H


Hailo models
Los modelos compatibles con Hailo utilizados durante el desarrollo incluyen:
yolov8m_h10.hef
ufld_v2_tu.hef


Traffic Sign Model
El modelo personalizado utilizado para señales de tráfico es:
traffic_sign_detector.pt


Los modelos no se incluyen directamente en el repositorio debido a su tamaño y/o distribución. Consulta la documentación correspondiente para obtenerlos e instalarlos.


📁 Repository Structure
road-ai-hailo10h/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── docs/
│
├── hardware/
│
├── models/
│
├── data/
│   ├── input/
│   └── output/
│
├── vehicle_detection/
│
├── traffic_sign_detection/
│   └── model/
│
├── lane_detection/
│
├── integration/
│
├── scripts/
│
└── results/


⚙️ Installation
La instalación y configuración completa del entorno se encuentra documentada en:
- [Hardware](docs/01-hardware.md)
- [Installation](docs/02-installation.md)
- [Hailo Setup](docs/03-hailo-setup.md)


▶️ Usage
Cada módulo puede ejecutarse de manera independiente.
Vehicle Detection
vehicle_detection/
└── traffic_detection_pipeline.py


Traffic Sign Detection
traffic_sign_detection/
├── process_image.py
└── process_video.py


Lane Detection
lane_detection/
├── lane_detection.py
└── lane_detection_utils.py


La documentación específica de cada módulo se encuentra en:
- [Vehicle Detection](docs/04-vehicle-detection.md)
- [Traffic Sign Detection](docs/05-traffic-sign-detection.md)
- [Lane Detection](docs/06-lane-detection.md)


📊 Performance
Durante las pruebas realizadas sobre Raspberry Pi 5 + Hailo-10H se obtuvieron aproximadamente los siguientes resultados:
| Modelo / Pipeline | Rendimiento |
|---|---:|
| YOLOv8m Hailo-10H | ~76 FPS |
| YOLO11m Hailo-10H | ~71 FPS |
| Lane Detection | ~13 FPS |


Los valores pueden variar dependiendo de:
- Resolución del video.
- Codec.
- Preprocesamiento.
- Postprocesamiento.
- Pipeline utilizado.
- Temperatura del sistema.
- Carga de CPU.


Los benchmarks completos se documentarán en:
docs/08-performance.md


🧪 Test Videos
Durante el desarrollo se utilizaron videos de prueba de carretera.
Manejando_en_carretera_UK.mp4
Manejando_en_carretera_UK_1080p30_h264.mp4
Video_carro_1.mp4

Los videos de prueba no se incluyen directamente en el repositorio.

Para utilizarlos, colócalos dentro de:
data/input/


🛠️ Project Status
Vehicle Detection
🟢 Implemented
Traffic Sign Detection
🟢 Implemented
Lane Detection
🟢 Implemented
Integrated Road AI Pipeline
🟡 In development


📚 Documentation
La documentación completa se encuentra en:
docs/

Incluye:
1. Hardware
2. Installation
3. Hailo Setup
4. Vehicle Detection
5. Traffic Sign Detection
6. Lane Detection
7. Integrated Pipeline
8. Performance


📄 License
This project is provided for educational and research purposes.
See the LICENSE file for details.
