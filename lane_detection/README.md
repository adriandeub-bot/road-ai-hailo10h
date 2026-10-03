# Lane Detection — Hailo-10H

Módulo de detección de carriles desarrollado para el proyecto **Road AI Hailo-10H**, utilizando una **Raspberry Pi 5** equipada con **Raspberry Pi AI HAT+ 2 (Hailo-10H, 40 TOPS)**.

El módulo utiliza el modelo **UFLD v2 TU (`ufld_v2_tu`)** para identificar las líneas de los carriles en video y generar una salida de video con las coordenadas detectadas.

> ⚠️ **Estado:** módulo experimental. La detección de carriles puede variar dependiendo de las condiciones de iluminación, perspectiva de la carretera, calidad del video y visibilidad de las líneas.

---

## Hardware

- Raspberry Pi 5 — 8 GB RAM
- Raspberry Pi AI HAT+ 2
- Hailo-10H — 40 TOPS
- Raspberry Pi OS / Debian 13 (Trixie), 64-bit

---

## Modelo

El módulo utiliza:

**UFLD v2 TU (`ufld_v2_tu`)**

En nuestra Raspberry Pi, el modelo Hailo-10H se encuentra en:

```text
/usr/local/hailo/resources/models/hailo10h/ufld_v2_tu.hef
```

El archivo `.hef` no se incluye en este repositorio.

Los archivos de modelos Hailo están excluidos mediante `.gitignore`.

---

## Estructura del módulo

```text
lane_detection/
├── README.md
├── requirements.txt
├── lane_detection.py
└── lane_detection_utils.py
```

### `lane_detection.py`

Script principal de ejecución.

Se encarga de:

- recibir el video de entrada;
- preparar los frames para inferencia;
- ejecutar la inferencia mediante Hailo;
- procesar los resultados;
- generar el video de salida con las coordenadas de los carriles.

### `lane_detection_utils.py`

Contiene las funciones de procesamiento específicas de la detección de carriles, incluyendo:

- procesamiento de resultados UFLD;
- redimensionamiento de frames;
- configuración del video de salida;
- cálculo de radios de visualización;
- validación de errores del procesamiento.

Este archivo contiene modificaciones realizadas específicamente para este proyecto.

---

## Modificaciones realizadas

La implementación utilizada en este proyecto parte del ejemplo de Lane Detection incluido en `hailo-apps`.

Se realizaron modificaciones en `lane_detection_utils.py` para mejorar el comportamiento observado durante las pruebas con videos de carretera.

### 1. Eliminación de los puntos de `col_lane_idx`

La implementación original utilizaba:

```python
col_lane_idx = [0, 3]
```

En nuestra versión se utiliza:

```python
col_lane_idx = []
```

Esto evita utilizar determinadas predicciones de columnas que no resultaban útiles para nuestro escenario de carretera.

### 2. Filtrado de puntos cercanos al horizonte

Se agregó un filtro para ignorar puntos demasiado cercanos al horizonte, donde las líneas de los carriles convergen y la predicción puede resultar menos estable.

El filtro utiliza el 55 % de la altura original del frame como límite:

```python
min_y = int(self.original_frame_height * 0.55)

if y_coord >= min_y:
    tmp.append((x_coord, y_coord))
```

El objetivo es reducir la presencia de puntos poco estables en la zona superior de la carretera.

---

## Dependencias

Las dependencias utilizadas por este módulo están especificadas en:

```text
requirements.txt
```

Actualmente son:

```text
tqdm
opencv-python<=4.10.0.84
numpy<2.0
python-dotenv
PyYAML
```

El módulo también requiere el entorno de software de **Hailo Apps / HailoRT** correspondiente al dispositivo Hailo-10H.

---

## Integración con Hailo Apps

`lane_detection.py` utiliza componentes del repositorio `hailo-apps`, entre ellos:

- `HailoInfer`
- configuración de Hailo Apps
- utilidades de logging
- gestión de argumentos
- colas de inferencia
- límites de trabajos de inferencia asíncrona

Por esta razón, los archivos incluidos en este repositorio representan el **módulo del proyecto**, pero no constituyen por sí solos una instalación independiente completa de Hailo Apps.

En la Raspberry Pi, el módulo se ejecuta dentro del entorno existente de:

```text
~/hailo-apps/
```

---

## Ejecución

Desde la Raspberry Pi, con el entorno de Hailo Apps configurado:

```bash
cd ~/hailo-apps/hailo_apps/python/standalone_apps/lane_detection
```

La ejecución puede realizarse especificando el modelo y el video de entrada:

```bash
python lane_detection.py \
    -n /usr/local/hailo/resources/models/hailo10h/ufld_v2_tu.hef \
    -i /ruta/al/video.mp4 \
    -o /ruta/de/salida
```

### Usando el Python del entorno del proyecto

En nuestro entorno se utiliza:

```bash
~/hailo-apps/venv_hailo_apps/bin/python
```

Por ejemplo:

```bash
~/hailo-apps/venv_hailo_apps/bin/python \
    ~/hailo-apps/hailo_apps/python/standalone_apps/lane_detection/lane_detection.py \
    -n /usr/local/hailo/resources/models/hailo10h/ufld_v2_tu.hef \
    -i /ruta/al/video.mp4 \
    -o /ruta/de/salida
```

---

## Argumentos principales

### `--hef-path` / `-n`

Especifica el modelo HEF que será utilizado.

Ejemplo:

```bash
-n /usr/local/hailo/resources/models/hailo10h/ufld_v2_tu.hef
```

### `--input` / `-i`

Especifica la fuente de entrada.

Puede utilizarse, dependiendo de la configuración del script:

- archivo de video;
- cámara;
- carpeta;
- RTSP;
- otros inputs soportados por Hailo Apps.

Ejemplo:

```bash
-i /home/proyectomundial/Videos/hailo/Manejando_en_carretera_UK_1080p30_h264.mp4
```

### `--output-dir` / `-o`

Especifica el directorio donde se almacenará el resultado.

Ejemplo:

```bash
-o ./output
```

### `--list-models`

Muestra los modelos disponibles para la aplicación.

```bash
python lane_detection.py --list-models
```

### `--list-inputs`

Muestra las fuentes de entrada predefinidas disponibles.

```bash
python lane_detection.py --list-inputs
```

### Ayuda

Para consultar todos los argumentos disponibles:

```bash
python lane_detection.py --help
```

---

## Ejemplo con un video de carretera

Ejemplo utilizando uno de los videos empleados durante las pruebas:

```bash
~/hailo-apps/venv_hailo_apps/bin/python \
    ~/hailo-apps/hailo_apps/python/standalone_apps/lane_detection/lane_detection.py \
    -n /usr/local/hailo/resources/models/hailo10h/ufld_v2_tu.hef \
    -i /home/proyectomundial/Videos/hailo/Manejando_en_carretera_UK_1080p30_h264.mp4 \
    -o ./output
```

Los videos utilizados durante las pruebas no se incluyen en este repositorio y están excluidos mediante `.gitignore`.

---

## Relación con otros módulos

Este módulo forma parte del sistema de análisis de carretera del proyecto **Road AI Hailo-10H**.

La arquitectura contempla diferentes capacidades de análisis:

```text
                    Video de carretera
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       Detección       Señales        Carriles
       vehículos       tráfico        UFLD v2 TU
             │             │             │
             ▼             ▼             ▼
       Tracking       Clasificación    Coordenadas
       vehículos      de señales       de carriles
```

La integración de estos módulos en un pipeline único se encuentra en desarrollo.

---

## Limitaciones actuales

La detección de carriles puede verse afectada por:

- iluminación deficiente;
- lluvia;
- sombras;
- líneas de carril desgastadas;
- carreteras sin marcas visibles;
- curvas pronunciadas;
- cambios bruscos de perspectiva;
- vehículos que ocultan las líneas;
- videos con resolución o calidad insuficiente.

El filtro implementado en `lane_detection_utils.py` está ajustado al comportamiento observado en nuestro escenario de pruebas y puede requerir modificaciones para otros tipos de carreteras o cámaras.

---

## Origen

La implementación base de este módulo proviene del ejemplo de **Lane Detection** incluido en el ecosistema `hailo-apps`.

Este repositorio conserva únicamente los archivos necesarios para documentar y reproducir la implementación utilizada en este proyecto, junto con las modificaciones específicas realizadas para nuestras pruebas.

---

## Licencia y atribución

Consultar las condiciones de licencia y los avisos correspondientes al código original de Hailo antes de redistribuir o utilizar este módulo fuera del contexto del proyecto.

---

## Estado del módulo

**Estado actual:** Experimental / En desarrollo

**Hardware probado:**

```text
Raspberry Pi 5 8GB
        +
Raspberry Pi AI HAT+ 2
        +
Hailo-10H 40 TOPS
```

**Modelo probado:**

```text
ufld_v2_tu.hef
```