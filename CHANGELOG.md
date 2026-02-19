# Changelog

Todas las versiones y cambios notables aplicados al proyecto **Isis**.

## [1.2.0] - 2026-02-19
### Añadido
- **Soporte Multi-Archivo**: Ahora es posible ocultar múltiples archivos simultáneamente en Imagen, Audio, Video y PDF.
- **Steganografía en PDF**: Implementación de técnica de overlay binario para ocultar datos en archivos PDF de forma robusta.
- **Steganografía en Video**: Sistema de firma `ISIS` para adjuntar y extraer archivos en contenedores de video (MP4, AVI, MOV).
- **Mejoras en Audio**: Motor de audio reescrito para soportar múltiples archivos y extracción masiva.
- **Rutas Absolutas**: La interfaz ahora muestra la ubicación exacta de los archivos extraídos para mayor comodidad del usuario.

### Corregido
- **WinError 32**: Solucionado el conflicto de acceso a archivos al procesar PDFs y Videos.
- **Corrupción de Extracción**: Corregido el error de "tamaño inválido" al extraer archivos de audio y video.
- **Estabilidad de GUI**: Limpieza de código muerto y optimización de la lógica de ejecución en `isis_gui.py`.

## [1.1.0] - 2026-02-18
### Añadido
- **Interfaz Gráfica (GUI)**: Implementación completa usando PyQt6 con un diseño moderno y oscuro.
- **Sistema de Temas**: Archivo `.qss` dedicado para una estética premium.
- **Steganografía en Audio**: Soporte inicial para archivos WAV usando LSB.

## [1.0.0] - Versión original
### Añadido
- Funcionalidad básica para ocultar archivos en imágenes.
- Cifrado AES-256 para protección de datos.
- Scripts base de CLI.
