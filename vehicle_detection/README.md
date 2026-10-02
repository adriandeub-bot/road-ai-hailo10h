# Vehicle Detection

Este módulo contiene los pipelines de detección y seguimiento de objetos desarrollados para el proyecto **Road AI Hailo-10H**.

La implementación utiliza **Hailo-10H** mediante `hailo-apps` y modelos de detección YOLO compatibles con el acelerador.

Actualmente se incluyen dos variantes:

- `traffic_detection_pipeline.py` — detección y tracking.
- `traffic_detection_save.py` — detección, tracking y exportación del video procesado.

> **Estado actual:** este módulo implementa detección y seguimiento de objetos. El conteo de vehículos, detección de señales de tránsito, análisis de carriles y la integración de todas estas funciones todavía se encuentran en desarrollo.

---

## Hardware

Hardware utilizado durante las pruebas:

- Raspberry Pi 5 8GB
- Raspberry Pi AI HAT+ 2
- Hailo-10H
- 40 TOPS
- Raspberry Pi OS / Debian 13 (Trixie) 64-bit

El acelerador Hailo se utiliza mediante PCIe.

---

## Software

El pipeline utiliza:

- Python 3.13.5
- `hailo-apps`
- GStreamer
- HailoRT
- Modelos YOLO compatibles con Hailo-10H

El entorno virtual utilizado en la Raspberry Pi es:

```text
/home/proyectomundial/hailo-apps/venv_hailo_apps
```

Para ejecutar los scripts se recomienda utilizar directamente el Python de este entorno.

---

## Modelos disponibles

El pipeline de detección para Hailo-10H actualmente reconoce los siguientes modelos.

### Modelo predeterminado

```text
yolov8m
```

### Modelos adicionales

```text
yolov5m_wo_spp
yolov5s
yolov5m
yolov6n
yolov7
yolov7x
yolov8s
yolov8n
yolov8l
yolov8x
yolov9c
yolov10n
yolov10s
yolov10b
yolov10x
yolov11n
yolov11s
yolov11m
yolov11l
yolov11x
```

Los modelos pueden seleccionarse mediante `--hef-path`.

Por ejemplo:

```bash
--hef-path yolov8m
```

o:

```bash
--hef-path yolov11m
```

Los modelos `.hef` no se almacenan en este repositorio.

---

# Pipeline

## `traffic_detection_pipeline.py`

Este script implementa el pipeline base de detección y seguimiento.

La estructura general es:

```text
Fuente de video
      │
      ▼
Inferencia Hailo-10H
      │
      ▼
Postprocesamiento
      │
      ▼
Tracker
      │
      ▼
Callback
      │
      ▼
Salida de video
```

El tracker utiliza:

```text
class_id = -1
keep_past_metadata = True
```

Esto permite realizar tracking sobre las clases detectadas por el modelo.

Actualmente el script utiliza `dummy_callback`, por lo que no contiene todavía una lógica personalizada de conteo o análisis de tráfico.

---

# Pipeline con exportación de video

## `traffic_detection_save.py`

Esta variante agrega una rama específica para guardar el resultado procesado.

La estructura es:

```text
Fuente de video
      │
      ▼
Inferencia Hailo-10H
      │
      ▼
Tracker
      │
      ▼
User Callback
      │
      ▼
      ├──────────────► Display
      │
      ▼
     Tee
      │
      └──────────────► Overlay
                              │
                              ▼
                         H.264 Encoder
                              │
                              ▼
                         Matroska (.mkv)
```

El pipeline utiliza:

- `INFERENCE_PIPELINE`
- `INFERENCE_PIPELINE_WRAPPER`
- `TRACKER_PIPELINE`
- `USER_CALLBACK_PIPELINE`
- `OVERLAY_PIPELINE`
- `x264enc`
- `h264parse`
- `matroskamux`
- `filesink`

La configuración actual de exportación utiliza H.264 con:

```text
bitrate = 8000
speed-preset = ultrafast
tune = zerolatency
threads = 4
```

El archivo de salida actualmente está definido dentro del script como:

```text
/home/proyectomundial/Videos/hailo/final_carro_2_detecciones.mkv
```

> El nombre y ubicación del archivo de salida están actualmente codificados directamente en el script y todavía no se exponen como argumento de línea de comandos.

---

# Uso

## 1. Activar el entorno virtual

En la Raspberry Pi:

```bash
source ~/hailo-apps/venv_hailo_apps/bin/activate
```

También es posible ejecutar los scripts directamente utilizando:

```bash
~/hailo-apps/venv_hailo_apps/bin/python
```

---

## 2. Consultar los modelos disponibles

```bash
python ~/hailo-apps/my_projects/traffic_detection_save.py --list-models
```

---

## 3. Consultar las opciones del programa

```bash
python ~/hailo-apps/my_projects/traffic_detection_save.py --help
```

Entre las opciones disponibles se encuentran:

```text
--input
--hef-path
--list-models
--batch-size
--show-fps
--frame-rate
--use-frame
--disable-sync
--disable-callback
--dump-dot
--print-pipeline
--enable-watchdog
--width
--height
--labels
--arch
--horizontal-mirror
--vertical-mirror
--labels-json
```

---

# Ejemplos

## Detección utilizando YOLOv8m

Ejemplo conceptual:

```bash
python ~/hailo-apps/my_projects/traffic_detection_save.py \
    --input /ruta/al/video.mp4 \
    --hef-path yolov8m \
    --arch hailo10h
```

## Detección utilizando YOLO11m

```bash
python ~/hailo-apps/my_projects/traffic_detection_save.py \
    --input /ruta/al/video.mp4 \
    --hef-path yolov11m \
    --arch hailo10h
```

El parámetro:

```text
--arch hailo10h
```

indica explícitamente que el modelo debe ejecutarse utilizando el acelerador Hailo-10H.

---

# Fuentes de entrada

El argumento `--input` admite diferentes tipos de fuentes, incluyendo:

- archivos de video;
- imágenes;
- carpetas de imágenes;
- cámaras USB;
- dispositivos `/dev/videoX`;
- cámaras Raspberry Pi;
- fuentes RTSP.

Ejemplo con un archivo de video:

```bash
--input /home/proyectomundial/Videos/hailo/video.mp4
```

---

# Rendimiento

Las pruebas realizadas anteriormente en el Hailo-10H han mostrado aproximadamente:

| Modelo | Rendimiento |
|---|---:|
| YOLOv8m | ~76 FPS |
| YOLO11m | ~71 FPS |

Estos valores corresponden a pruebas de inferencia realizadas en el hardware utilizado en este proyecto y no representan necesariamente el rendimiento final del pipeline completo con decodificación, tracking, overlay y codificación de video.

---

# Limitaciones actuales

Este módulo todavía no implementa de forma integrada:

- conteo de vehículos;
- clasificación específica de vehículos para análisis de tráfico;
- detección de señales de tránsito dentro del mismo pipeline;
- reconocimiento de placas;
- detección de carriles;
- fusión de detección de vehículos + señales + carriles;
- generación de estadísticas de tráfico.

Estas funciones forman parte de las siguientes etapas del proyecto.

---

# Próximos pasos

La evolución prevista del módulo es:

```text
Vehicle Detection
        │
        ├──► Vehicle Tracking
        │
        ├──► Vehicle Counting
        │
        ├──► Traffic Sign Detection
        │
        ├──► Lane Detection
        │
        └──► Integrated Road Analysis
```

El objetivo final es construir un pipeline de análisis de carretera ejecutado localmente en Raspberry Pi 5 + Hailo-10H, aprovechando la aceleración de Edge AI.

---

# Archivos

```text
vehicle_detection/
├── README.md
├── traffic_detection_pipeline.py
└── traffic_detection_save.py
```

## Descripción

| Archivo | Función |
|---|---|
| `traffic_detection_pipeline.py` | Pipeline de detección y tracking |
| `traffic_detection_save.py` | Pipeline de detección, tracking y exportación de video |
| `README.md` | Documentación del módulo |
```

### Después de guardarlo

No hagas todavía el commit.

En **PowerShell**, ejecutaremos solamente:

```powershell
git diff -- vehicle_detection/README.md
```

Esto nos permitirá revisar exactamente qué quedó documentado antes de incorporarlo al repositorio.