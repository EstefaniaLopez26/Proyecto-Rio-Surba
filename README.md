# 💧 EcoSurba — Plataforma de Inteligencia Hídrica

Sistema web de monitoreo ambiental y ciencia ciudadana diseñado para la evaluación en tiempo real de la calidad del agua en la cuenca del **Río Surba (Duitama, Boyacá, Colombia)**.

## 🚀 Características Principales
* **Diagnóstico Hídrico Integrado:** Combina parámetros fisicoquímicos tomados en campo (`pH`, `Temperatura` y `Turbidez`) con un modelo de visión artificial (**TensorFlow / MobileNetV2**) para clasificar el estado de la muestra (`NORMAL`, `ATENCIÓN` o `ALTERACIÓN`).
* **Sistema de Alertas Tempranas:** Genera y registra automáticamente alertas ambientales cuando se detectan anomalías críticas en cualquiera de las estaciones oficiales (*Sector La Trinidad*, *Vereda Higueras* y *Surba y Bonza*).
* **Persistencia Relacional:** Base de datos estructurada en **MySQL** con trazabilidad de estaciones georreferenciadas, historial longitudinal de muestras, evidencias fotográficas y buzón de valoración comunitaria.
* **Diseño Responsivo:** Interfaz adaptada para uso tanto en escritorio como en dispositivos móviles directamente en campo.

## 🛠️ Stack Tecnológico
* **Frontend & Backend:** Python, Streamlit
* **Inteligencia Artificial:** TensorFlow / Keras (MobileNetV2), NumPy, Pillow
* **Base de Datos:** MySQL (`mysql-connector-python`), Pandas

## ⚙️ Ejecución Local
1. Clonar el repositorio e instalar dependencias:
   ```bash
   pip install -r requirements.txt
