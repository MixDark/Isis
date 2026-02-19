# 👁️ Isis - Esteganografía avanzada

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Isis** es una suite de esteganografía avanzada y profesional que permite ocultar información y archivos dentro de diversos portadores multimedia. Diseñada con un enfoque en la seguridad y la experiencia de usuario, Isis utiliza cifrado de grado militar para proteger tus secretos.

---

## 🚀 Características principales

- **🖼️ Imágenes (LSB)**: Oculta texto o archivos en imágenes PNG sin distorsión visual.
- **🎵 Audio (WAV/MP3)**: Implementación de LSB en audio para ocultar datos de forma imperceptible.
- **🎬 Video (Overlay)**: Sistema robusto para adjuntar archivos en portadores de video (MP4, AVI, MOV).
- **📄 PDF (Binary Append)**: Oposición de datos en documentos PDF sin afectar su lectura.
- **📂 Multi-Archivo**: Soporte único para ocultar y extraer múltiples archivos a la vez.
- **🔐 Seguridad AES-256**: Opción de cifrar todo el contenido con una contraseña segura.
- **🎨 Interfaz Premium**: GUI moderna, oscura y optimizada para el flujo de trabajo rápido.

---

## Requerimientos

<img width="1147" height="814" alt="image" src="https://github.com/user-attachments/assets/bea90ede-bbfb-453a-967c-13d9dd29fc6d" />  

<img width="1137" height="807" alt="image" src="https://github.com/user-attachments/assets/9283bf1e-4ba0-4b83-94c7-d1447b52ecf2" />


## 🛠️ Requerimientos

- **Python 3.10+**
- **PyQt6** (Interfaz gráfica)
- **OpenCV** (Procesamiento de imagen)
- **PyCryptodome** (Cifrado AES)
- **Pydub** (Procesamiento de audio)
- **FFmpeg**: Los binarios de FFmpeg no se incluyen en este repositorio debido a su tamaño. **Debe descargarlos desde [este enlace de Google Drive](https://drive.google.com/drive/folders/1LldbJ0mdY4YXQpSTvOXh2dFk8FeLKUj-?usp=sharing)** y colocar los archivos `ffmpeg.exe`, `ffplay.exe` y `ffprobe.exe` directamente en la carpeta raíz del proyecto.

---

## 📥 Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/MixDark/Isis.git
   cd Isis
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación:**
   ```bash
   python isis_gui.py
   ```

---

## 📖 Modo de Uso

### Ocultar archivos
1. Selecciona la **Acción** deseada (ej. Ocultar archivo en imagen).
2. Elige el archivo **Portador** (el que esconderá la información).
3. Selecciona los archivos a **Ocultar** (puedes elegir varios archivos a la vez).
4. Elige la ruta de **Salida**.
5. (Opcional) Ingresa una **Contraseña**.
6. Haz clic en **Ejecutar**.

### Extraer archivos
1. Selecciona la acción de **Extracción** correspondiente.
2. Selecciona el archivo que contiene los datos ocultos.
3. Ingresa la contraseña si fue utilizada al ocultar.
4. El programa extraerá automáticamente todos los archivos en el directorio del portador.

---

## ⚠️ Descargo de responsabilidad

Este software ha sido creado con fines **educativos y de ciberseguridad ética**. El uso de esta herramienta para actividades maliciosas es responsabilidad exclusiva del usuario final. Asegúrate de cumplir con las leyes locales de privacidad y protección de datos.

---

## 📝 Contribuciones

Las contribuciones son bienvenidas. Si tienes ideas para nuevos formatos de portadores o mejoras en el cifrado, no dudes en abrir un *Issue* o enviar un *Pull Request*.

---

**Desarrollado para la comunidad de ciberseguridad.**
