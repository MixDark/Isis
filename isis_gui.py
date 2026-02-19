from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QTextEdit, QMessageBox, QComboBox, QCheckBox, QInputDialog, QFrame, QSizePolicy
)
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtCore import Qt
import sys
import os

class IsisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Isis - Esteganografía avanzada')
        
        # Tamaño fijo para que coincida con la imagen y deshabilitar redimensión
        self.setFixedSize(920, 620)
        
        # Deshabilitar botón de maximizar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet("font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 13px;")
        
        self.init_theme()
        self.init_ui()
        self.center()

    def center(self):
        # Centrar la ventana en la pantalla
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_theme(self):
        # Tema Fusion oscuro
        QApplication.setStyle("Fusion")
        from PyQt6.QtGui import QPalette, QColor
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(35, 38, 41))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 49, 54))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 38, 41))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(58, 63, 68))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(58, 63, 68))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(126, 207, 255))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 38, 41))
        QApplication.setPalette(dark_palette)

        # Cargar QSS desde archivo externo
        import os
        qss_path = os.path.join(os.path.dirname(__file__), "isis_style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            self.setStyleSheet("")

    def init_ui(self):
        # Panel principal y lateral
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Panel lateral (opciones)
        side_panel = QFrame()
        side_panel.setObjectName("sidePanel")
        side_layout = QVBoxLayout(side_panel)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Combo de acciones
        self.combo_accion = QComboBox()
        self.combo_accion.addItems([
            "Ocultar texto en imagen",
            "Extraer texto de imagen",
            "Ocultar archivo en audio",
            "Extraer archivo de audio",
            "Ocultar archivo en video",
            "Extraer archivo de video",
            "Ocultar archivo en PDF",
            "Extraer archivo de PDF"
        ])
        self.combo_accion.currentIndexChanged.connect(self.actualizar_formulario)
        side_layout.addWidget(QLabel("Acción:"))
        side_layout.addWidget(self.combo_accion)

        # Panel de formulario dinámico
        self.form_panel = QFrame()
        self.form_panel.setObjectName("formPanel")
        self.form_layout = QVBoxLayout(self.form_panel)
        self.form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        side_layout.addWidget(self.form_panel)

        # Botón ejecutar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        self.btn_ejecutar = QPushButton("Ejecutar")
        self.btn_ejecutar.setFixedWidth(100) 
        self.btn_ejecutar.clicked.connect(self.ejecutar_accion)
        btn_layout.addWidget(self.btn_ejecutar)
        btn_layout.addStretch(1)
        side_layout.addLayout(btn_layout)

        # Espaciador
        side_layout.addStretch(1)

        # Panel principal (resultados)
        main_panel = QFrame()
        main_panel.setObjectName("mainPanel")
        main_panel_layout = QVBoxLayout(main_panel)
        main_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlaceholderText("Resultados y mensajes...")
        main_panel_layout.addWidget(QLabel("Resultados:"))
        main_panel_layout.addWidget(self.result)

        # Agregar paneles al layout principal
        main_layout.addWidget(side_panel, 2)
        main_layout.addWidget(main_panel, 3)

        # Inicializar el formulario según la acción seleccionada
        self.actualizar_formulario()

    def limpiar_formulario(self):
        # Elimina widgets previos del formulario
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def actualizar_formulario(self):
        self.limpiar_formulario()
        accion = self.combo_accion.currentText()
        self.campos = {}
        if accion == "Ocultar texto en imagen":
            self.campos['img'] = self._crear_selector_archivo("Selecciona la imagen portadora", "Imagen PNG (*.png)")
            self.campos['out'] = self._crear_selector_guardar("Guardar imagen de salida", "Imagen PNG (*.png)")
            self.campos['texto'] = self._crear_texto_multilinea("Texto a ocultar")
            self.campos['contraseña'] = self._crear_contraseña()
        elif accion == "Extraer texto de imagen":
            self.campos['img'] = self._crear_selector_archivo("Selecciona la imagen con texto oculto", "Imagen PNG (*.png)")
            self.campos['contraseña'] = self._crear_contraseña(pregunta="¿El texto está protegido con contraseña?")
        elif accion == "Ocultar archivo en audio":
            self.campos['audio'] = self._crear_selector_archivo("Selecciona el audio portador (WAV o MP3)", "Audio (*.wav *.mp3)")
            self.campos['out'] = self._crear_selector_guardar("Guardar audio de salida", "Audio (*.wav *.mp3)")
            self.campos['file'] = self._crear_selector_archivo("Selecciona el archivo a ocultar", "Todos los archivos (*)")
            self.campos['contraseña'] = self._crear_contraseña()
        elif accion == "Extraer archivo de audio":
            self.campos['audio'] = self._crear_selector_archivo("Selecciona el audio con datos ocultos (WAV o MP3)", "Audio (*.wav *.mp3)")
            self.campos['contraseña'] = self._crear_contraseña(pregunta="¿El archivo está protegido con contraseña?")
        elif accion == "Ocultar archivo en video":
            self.campos['video'] = self._crear_selector_archivo("Selecciona el video portador", "Video (*.mp4 *.avi *.mov)")
            self.campos['out'] = self._crear_selector_guardar("Guardar video de salida", "Video (*.mp4 *.avi *.mov)")
            self.campos['file'] = self._crear_selector_archivo("Selecciona el archivo a ocultar", "Todos los archivos (*)")
            self.campos['contraseña'] = self._crear_contraseña()
        elif accion == "Extraer archivo de video":
            self.campos['video'] = self._crear_selector_archivo("Selecciona el video con datos ocultos", "Video (*.mp4 *.avi *.mov)")
            self.campos['contraseña'] = self._crear_contraseña(pregunta="¿El archivo está protegido con contraseña?")
        elif accion == "Ocultar archivo en PDF":
            self.campos['pdf'] = self._crear_selector_archivo("Selecciona el PDF portador", "PDF (*.pdf)")
            self.campos['out'] = self._crear_selector_guardar("Guardar PDF de salida", "PDF (*.pdf)")
            self.campos['file'] = self._crear_selector_archivo("Selecciona el archivo a ocultar", "Todos los archivos (*)")
            self.campos['contraseña'] = self._crear_contraseña()
        elif accion == "Extraer archivo de PDF":
            self.campos['pdf'] = self._crear_selector_archivo("Selecciona el PDF con datos ocultos", "PDF (*.pdf)")
            self.campos['contraseña'] = self._crear_contraseña(pregunta="¿El archivo está protegido con contraseña?")

    def _crear_selector_archivo(self, label, filtro):
        layout = QVBoxLayout() # Cambiado a vertical
        lbl = QLabel(label)
        
        sub_layout = QHBoxLayout() # Layout para combo textbox + botón
        edit = QLineEdit()
        btn = QPushButton("Examinar")
        
        def seleccionar():
            paths, _ = QFileDialog.getOpenFileNames(self, label, '', filtro)
            if paths:
                edit.setProperty("full_paths", paths)
                if len(paths) == 1:
                    edit.setText(os.path.basename(paths[0]))
                else:
                    edit.setText(f"{len(paths)} archivos seleccionados")
        btn.clicked.connect(seleccionar)
        
        layout.addWidget(lbl)
        sub_layout.addWidget(edit)
        sub_layout.addWidget(btn)
        layout.addLayout(sub_layout)
        
        cont = QWidget()
        cont.setLayout(layout)
        self.form_layout.addWidget(cont)
        return edit

    def _crear_selector_guardar(self, label, filtro):
        layout = QVBoxLayout() # Cambiado a vertical
        lbl = QLabel(label)
        
        sub_layout = QHBoxLayout() # Layout para combo textbox + botón
        edit = QLineEdit()
        btn = QPushButton("Guardar")
        
        def seleccionar():
            path, _ = QFileDialog.getSaveFileName(self, label, '', filtro)
            if path:
                edit.setProperty("full_path", path)
                edit.setText(os.path.basename(path))
        btn.clicked.connect(seleccionar)
        
        layout.addWidget(lbl)
        sub_layout.addWidget(edit)
        sub_layout.addWidget(btn)
        layout.addLayout(sub_layout)
        
        cont = QWidget()
        cont.setLayout(layout)
        self.form_layout.addWidget(cont)
        return edit

    def _crear_texto_multilinea(self, label):
        lbl = QLabel(label)
        edit = QTextEdit()
        self.form_layout.addWidget(lbl)
        self.form_layout.addWidget(edit)
        return edit

    def _crear_contraseña(self, pregunta=None):
        if pregunta:
            lbl = QLabel(pregunta)
            self.form_layout.addWidget(lbl)
        edit = QLineEdit()
        edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.setPlaceholderText("Contraseña (opcional)")
        self.form_layout.addWidget(edit)
        return edit

    def _get_path(self, campo_key):
        """Obtiene la ruta única de un campo."""
        widget = self.campos.get(campo_key)
        if not widget: return ""
        paths = widget.property("full_paths")
        if paths and len(paths) > 0:
            return paths[0]
        full_path = widget.property("full_path")
        return full_path if full_path else widget.text()

    def _get_paths(self, campo_key):
        """Obtiene la lista de todas las rutas seleccionadas."""
        widget = self.campos.get(campo_key)
        if not widget: return []
        paths = widget.property("full_paths")
        if paths: return paths
        path = self._get_path(campo_key)
        return [path] if path else []

    def ejecutar_accion(self):
        accion = self.combo_accion.currentText()
        try:
            if accion == "Ocultar texto en imagen":
                img_path = self._get_path('img')
                out_path = self._get_path('out')
                texto = self.campos['texto'].toPlainText()
                contraseña = self.campos['contraseña'].text() or None
                if not img_path or not out_path or not texto:
                    self.result.append('Completa los campos requeridos.')
                    return
                import cv2
                from isis import LSBSteg, cifrar_datos
                in_img = cv2.imread(img_path)
                steg = LSBSteg(in_img)
                data = texto.encode('utf-8')
                if contraseña: data = cifrar_datos(data, contraseña)
                res = steg.encode_binary([("texto.txt", data)])
                cv2.imwrite(out_path, res)
                self.result.append(f'<b>Éxito:</b> Texto ocultado en {os.path.basename(out_path)}')

            elif accion == "Extraer texto de imagen":
                img_path = self._get_path('img')
                contraseña = self.campos['contraseña'].text() or None
                if not img_path:
                    self.result.append('Selecciona la imagen.')
                    return
                import cv2
                from isis import LSBSteg, descifrar_datos
                in_img = cv2.imread(img_path)
                steg = LSBSteg(in_img)
                try:
                    archivos = steg.decode_binary()
                    if not archivos:
                        self.result.append('No se encontraron datos ocultos.')
                        return
                    for filename, raw in archivos:
                        if contraseña: raw = descifrar_datos(raw, contraseña)
                        texto = raw.decode('utf-8', errors='replace')
                        self.result.append(f'<b>Texto extraído ({filename}):</b>\n{texto}')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Ocultar archivo en imagen":
                img_path = self._get_path('img')
                out_path = self._get_path('out')
                files_to_hide = self._get_paths('file')
                contraseña = self.campos['contraseña'].text() or None
                if not img_path or not out_path or not files_to_hide:
                    self.result.append('Completa todos los campos.')
                    return
                import cv2
                from isis import LSBSteg, cifrar_datos
                in_img = cv2.imread(img_path)
                steg = LSBSteg(in_img)
                paquete = []
                for f_path in files_to_hide:
                    with open(f_path, "rb") as f:
                        d = f.read()
                    if contraseña: d = cifrar_datos(d, contraseña)
                    paquete.append((os.path.basename(f_path), d))
                res = steg.encode_binary(paquete)
                cv2.imwrite(out_path, res)
                self.result.append(f'<b>Éxito:</b> {len(files_to_hide)} archivos ocultados en {os.path.basename(out_path)}')

            elif accion == "Extraer archivo de imagen":
                img_path = self._get_path('img')
                contraseña = self.campos['contraseña'].text() or None
                if not img_path:
                    self.result.append('Selecciona la imagen.')
                    return
                import cv2
                from isis import LSBSteg, descifrar_datos
                in_img = cv2.imread(img_path)
                steg = LSBSteg(in_img)
                try:
                    archivos = steg.decode_binary()
                    if not archivos:
                        self.result.append('No se encontraron datos.')
                        return
                    base_dir = os.path.dirname(os.path.abspath(img_path))
                    for filename, raw in archivos:
                        if contraseña: raw = descifrar_datos(raw, contraseña)
                        save_path = os.path.join(base_dir, filename)
                        with open(save_path, "wb") as f: f.write(raw)
                        self.result.append(f'<b>Extraído:</b> <font color="#7ecfff">{filename}</font>')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Ocultar archivo en audio":
                audio_path = self._get_path('audio')
                out_path = self._get_path('out')
                files_to_hide = self._get_paths('file')
                contraseña = self.campos['contraseña'].text() or None
                if not audio_path or not out_path or not files_to_hide:
                    self.result.append('Completa los campos requeridos.')
                    return
                from isis import ocultar_archivos_en_audio
                try:
                    ocultar_archivos_en_audio(audio_path, files_to_hide, out_path, contraseña)
                    self.result.append(f'<b>Éxito:</b> {len(files_to_hide)} archivos ocultos en el audio.')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Extraer archivo de audio":
                audio_path = self._get_path('audio')
                contraseña = self.campos['contraseña'].text() or None
                from isis import extraer_archivo_de_audio
                try:
                    # El motor de audio ya guarda en disco
                    res = extraer_archivo_de_audio(audio_path, contraseña)
                    self.result.append(f'<b>Éxito:</b> Archivos extraídos en la carpeta de origen.')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Ocultar archivo en video":
                video_path = self._get_path('video')
                out_path = self._get_path('out')
                files_to_hide = self._get_paths('file')
                contraseña = self.campos['contraseña'].text() or None
                if not video_path or not out_path or not files_to_hide:
                    self.result.append('Completa los campos.'); return
                from isis import ocultar_archivos_en_video
                try:
                    ocultar_archivos_en_video(video_path, files_to_hide, out_path, contraseña)
                    self.result.append(f'<b>Éxito:</b> {len(files_to_hide)} archivos ocultados en el video.')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Extraer archivo de video":
                video_path = self._get_path('video')
                contraseña = self.campos['contraseña'].text() or None
                from isis import extraer_archivos_de_video
                try:
                    res = extraer_archivos_de_video(video_path, contraseña, os.path.dirname(video_path))
                    self.result.append(f'<b>Éxito:</b> {len(res)} archivos extraídos en la carpeta del video.')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Ocultar archivo en PDF":
                pdf_path = self._get_path('pdf')
                out_path = self._get_path('out')
                files_to_hide = self._get_paths('file')
                contraseña = self.campos['contraseña'].text() or None
                if not pdf_path or not out_path or not files_to_hide:
                    self.result.append('Completa los campos.'); return
                from isis import ocultar_archivos_en_pdf
                try:
                    ocultar_archivos_en_pdf(pdf_path, files_to_hide, out_path, contraseña)
                    self.result.append(f'<b>Éxito:</b> {len(files_to_hide)} archivos ocultados en el PDF.')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')

            elif accion == "Extraer archivo de PDF":
                pdf_path = self._get_path('pdf')
                contraseña = self.campos['contraseña'].text() or None
                from isis import extraer_archivo_de_pdf
                try:
                    res = extraer_archivo_de_pdf(pdf_path, contraseña)
                    self.result.append(f'<b>Éxito:</b> Archivos extraídos correctamente.')
                except Exception as e:
                    self.result.append(f'<font color="red">Error: {e}</font>')
        except Exception as e:
            self.result.append(f"<font color='red'>Error crítico: {e}</font>")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = IsisGUI()
    gui.show()
    sys.exit(app.exec())
