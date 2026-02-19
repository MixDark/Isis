# === FUNCIONES DE ALTO NIVEL PARA LA GUI ===
def ocultar_archivo_en_imagen(imagen_path, archivo_path, salida_path, password=None):
    """Oculta un archivo en una imagen (PNG) usando LSB. Si se da password, cifra el archivo."""
    img = cv2.imread(imagen_path)
    if img is None:
        raise SteganographyException("No se pudo abrir la imagen portadora.")
    with open(archivo_path, "rb") as f:
        data = f.read()
    if password:
        data = cifrar_datos(data, password)
    steg = LSBSteg(img)
    res = steg.encode_binary(data, filename=os.path.basename(archivo_path))
    cv2.imwrite(salida_path, res)
    return True

def extraer_archivo_de_imagen(imagen_path, password=None, ruta_salida=None):
    """Extrae un archivo oculto en una imagen (PNG) usando LSB. Si password, descifra."""
    img = cv2.imread(imagen_path)
    if img is None:
        raise SteganographyException("No se pudo abrir la imagen.")
    steg = LSBSteg(img)
    filename, raw = steg.decode_binary()
    if not raw:
        raise SteganographyException("No se pudo extraer ningún dato. ¿Seguro que la imagen tiene datos ocultos?")
    advertencia = None
    if password:
        if es_dato_cifrado(raw):
            raw = descifrar_datos(raw, password)
        else:
            advertencia = "El dato extraído no está cifrado. Se extrajo sin descifrar."
    if ruta_salida is None:
        ruta_salida = filename
    with open(ruta_salida, "wb") as f:
        f.write(raw)
    if advertencia:
        return f"{ruta_salida} (ADVERTENCIA: {advertencia})"
    return ruta_salida

def ocultar_texto_en_imagen(imagen_path, texto, salida_path, password=None):
    """Oculta un texto en una imagen (PNG) usando LSB. Si password, cifra el texto."""
    img = cv2.imread(imagen_path)
    if img is None:
        raise SteganographyException("No se pudo abrir la imagen portadora.")
    data = texto.encode("utf-8")
    if password:
        data = cifrar_datos(data, password)
    steg = LSBSteg(img)
    res = steg.encode_binary(data, filename="texto.txt")
    cv2.imwrite(salida_path, res)
    return True

def extraer_texto_de_imagen(imagen_path, password=None):
    """Extrae texto oculto en una imagen (PNG) usando LSB. Si password, descifra."""
    img = cv2.imread(imagen_path)
    if img is None:
        raise SteganographyException("No se pudo abrir la imagen.")
    steg = LSBSteg(img)
    filename, raw = steg.decode_binary()
    if not raw:
        raise SteganographyException("No se pudo extraer ningún dato. ¿Seguro que la imagen tiene datos ocultos?")
    advertencia = None
    if password:
        if es_dato_cifrado(raw):
            raw = descifrar_datos(raw, password)
        else:
            advertencia = "El dato extraído no está cifrado. Se extrajo sin descifrar."
    resultado = raw.decode("utf-8", errors="replace")
    if advertencia:
        return f"{resultado}\n\nADVERTENCIA: {advertencia}"
    return resultado

def ocultar_archivos_en_audio(audio_path, lista_archivos, salida_path, password=None):
    """Oculta múltiples archivos en un audio."""
    try:
        sound = AudioSegment.from_file(audio_path)
    except Exception as e:
        raise SteganographyException(f"Error cargando audio: {e}")
        
    frames = bytearray(sound.raw_data)
    
    # Header global: [1 byte num_files]
    payload = bytes([len(lista_archivos)])
    
    for archivo_path in lista_archivos:
        with open(archivo_path, "rb") as f:
            data = f.read()
        if password:
            data = cifrar_datos(data, password)
            
        name = os.path.basename(archivo_path).encode('utf-8')[:255]
        payload += bytes([len(name)]) + name + struct.pack(">I", len(data)) + data
        
    if len(payload) * 8 > len(frames):
        raise SteganographyException("Capacidad de audio superada.")
        
    for i in range(len(payload)):
        byte = payload[i]
        for bit in range(8):
            frames[i*8+bit] = (frames[i*8+bit] & 0xFE) | ((byte >> (7-bit)) & 1)
            
    new_sound = AudioSegment(data=bytes(frames), sample_width=sound.sample_width, frame_rate=sound.frame_rate, channels=sound.channels)
    if not salida_path.lower().endswith('.wav'): salida_path += ".wav"
    new_sound.export(salida_path, format="wav")
    return True

def extraer_archivo_de_audio(audio_path, password=None, output_dir=None):
    """Extrae múltiples archivos ocultos en un audio usando LSB de forma robusta."""
    try:
        sound = AudioSegment.from_file(audio_path)
    except Exception as e:
        raise SteganographyException(f"No se pudo cargar el audio: {e}")
        
    frames = bytearray(sound.raw_data)
    total_bits = len(frames)
    if total_bits < 8: raise SteganographyException("Audio inválido (muy corto).")
        
    # 1. Leer número de archivos (1 byte / 8 bits)
    num_files = 0
    for i in range(8):
        num_files = (num_files << 1) | (int(frames[i]) & 1)
        
    if num_files == 0 or num_files > 255:
        raise SteganographyException("No se detectaron archivos Isis válidos.")
        
    results = []
    current_bit = 8
    
    base_dir = output_dir or os.path.dirname(os.path.abspath(audio_path))
    
    for _ in range(num_files):
        # 2. Leer name_len (8 bits)
        if current_bit + 8 > total_bits: break
        name_len = 0
        for i in range(8):
            name_len = (name_len << 1) | (int(frames[current_bit+i]) & 1)
        current_bit += 8
        
        # 3. Leer nombre
        if current_bit + name_len * 8 > total_bits: break
        name_bytes = bytearray()
        for j in range(name_len):
            b = 0
            for k in range(8):
                b = (b << 1) | (int(frames[current_bit + j*8 + k]) & 1)
            name_bytes.append(b)
        filename = name_bytes.decode('utf-8', errors='replace').replace('\x00', '').strip()
        current_bit += name_len * 8
        
        # 4. Leer data_len (32 bits)
        if current_bit + 32 > total_bits: break
        size_bytes = bytearray()
        for i in range(4):
            b = 0
            for k in range(8):
                b = (b << 1) | (int(frames[current_bit + i*8 + k]) & 1)
            size_bytes.append(b)
        size = struct.unpack(">I", size_bytes)[0]
        current_bit += 32
        
        # Validación de seguridad
        if current_bit + size * 8 > total_bits or size > 100*1024*1024:
            continue # O lanzar error si es crítico
            
        # 5. Leer datos
        data_bytes = bytearray()
        for i in range(size):
            b = 0
            for k in range(8):
                b = (b << 1) | (int(frames[current_bit + i*8 + k]) & 1)
            data_bytes.append(b)
        current_bit += size * 8
        
        data = bytes(data_bytes)
        if password and es_dato_cifrado(data):
            try:
                data = descifrar_datos(data, password)
            except:
                # Si falla descifrado guardamos original o saltamos
                pass
                
        if not filename: filename = f"extraido_{len(results)}.bin"
        save_path = os.path.join(base_dir, filename)
        with open(save_path, "wb") as f:
            f.write(data)
        results.append(save_path)
            
    return results

def ocultar_archivos_en_video(video_path, archivos_a_ocultar, salida_path, password=None):
    """Oculta múltiples archivos en un video usando la técnica de overlay."""
    try:
        # Copiamos el video original al destino solo una vez
        if os.path.abspath(video_path) != os.path.abspath(salida_path):
            shutil.copy2(video_path, salida_path)
        
        for archivo_path in archivos_a_ocultar:
            with open(archivo_path, "rb") as f:
                data = f.read()
            if password:
                data = cifrar_datos(data, password)
                
            filename = os.path.basename(archivo_path).encode('utf-8')
            if len(filename) > 255: filename = filename[:255]
            
            payload = b"ISIS" + bytes([len(filename)]) + filename + struct.pack(">I", len(data)) + data
            
            with open(salida_path, "ab") as f:
                f.write(payload)
        return True
    except Exception as e:
        raise SteganographyException(f"Error al procesar video: {e}")

def ocultar_archivo_en_video(video_path, archivo_path, salida_path, password=None):
    """Wrapper para compatibilidad."""
    return ocultar_archivos_en_video(video_path, [archivo_path], salida_path, password)

def extraer_archivos_de_video(video_path, password=None, output_dir=None):
    """Busca y extrae todos los archivos que tengan la firma ISIS en un video."""
    try:
        with open(video_path, "rb") as f:
            content = f.read()
            
        results = []
        # Buscamos todas las ocurrencias de ISIS
        start = 0
        while True:
            pos = content.find(b"ISIS", start)
            if pos == -1: break
            
            offset = pos + 4
            name_len = content[offset]
            offset += 1
            filename = content[offset:offset+name_len].decode('utf-8', errors='replace')
            offset += name_len
            size = struct.unpack(">I", content[offset:offset+4])[0]
            offset += 4
            data = content[offset:offset+size]
            
            if password and es_dato_cifrado(data):
                try: data = descifrar_datos(data, password)
                except: pass # Si falla el descifrado guardamos el original
                
            save_path = os.path.join(output_dir or ".", filename)
            with open(save_path, "wb") as f: f.write(data)
            results.append(save_path)
            start = offset + size
            
        return results
    except Exception as e:
        raise SteganographyException(f"Error Video: {e}")

def ocultar_archivos_en_pdf(pdf_path, archivos_a_ocultar, salida_path, password=None):
    """Oculta múltiples archivos en un PDF usando la técnica de overlay."""
    try:
        if os.path.abspath(pdf_path) != os.path.abspath(salida_path):
            shutil.copy2(pdf_path, salida_path)
            
        for archivo_path in archivos_a_ocultar:
            with open(archivo_path, "rb") as f:
                data = f.read()
            if password:
                data = cifrar_datos(data, password)
                
            filename = os.path.basename(archivo_path).encode('utf-8')
            if len(filename) > 255: filename = filename[:255]
            
            payload = b"ISIS" + bytes([len(filename)]) + filename + struct.pack(">I", len(data)) + data
            
            with open(salida_path, "ab") as f:
                f.write(payload)
        return True
    except Exception as e:
        raise SteganographyException(f"Error al procesar PDF: {e}")

def ocultar_archivo_en_pdf(pdf_path, archivo_path, salida_path, password=None):
    """Wrapper para compatibilidad."""
    return ocultar_archivos_en_pdf(pdf_path, [archivo_path], salida_path, password)

def extraer_archivos_de_pdf(pdf_path, password=None, output_dir=None):
    """Busca y extrae todos los archivos que tengan la firma ISIS en un PDF."""
    try:
        with open(pdf_path, "rb") as f:
            content = f.read()
            
        results = []
        start = 0
        while True:
            pos = content.find(b"ISIS", start)
            if pos == -1: break
            
            offset = pos + 4
            if offset >= len(content): break
            name_len = content[offset]
            offset += 1
            filename = content[offset:offset+name_len].decode('utf-8', errors='replace')
            offset += name_len
            if offset + 4 > len(content): break
            size = struct.unpack(">I", content[offset:offset+4])[0]
            offset += 4
            data = content[offset:offset+size]
            
            if password and es_dato_cifrado(data):
                try: data = descifrar_datos(data, password)
                except: pass
                
            save_path = os.path.join(output_dir or os.path.dirname(os.path.abspath(pdf_path)), filename)
            with open(save_path, "wb") as f: f.write(data)
            results.append(save_path)
            start = offset + size
            
        if not results:
            raise SteganographyException("No se encontraron archivos ocultos con la firma ISIS.")
        return results
    except Exception as e:
        raise SteganographyException(f"Error PDF: {e}")

def extraer_archivo_de_pdf(pdf_path, password=None, output_dir=None):
    """Wrapper para compatibilidad con la GUI actual."""
    return extraer_archivos_de_pdf(pdf_path, password, output_dir)
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os
import shutil
import wave
import tempfile
from pydub import AudioSegment
from pydub.utils import which
AudioSegment.converter = which('ffmpeg.exe')
from PyPDF2 import PdfReader, PdfWriter
import logging
import struct


class SteganographyException(Exception):

    pass



def descifrar_datos(data, password):
    """
    Descifra los datos usando AES-256 en modo CBC con una contraseña.
    Espera: salt (16) + iv (16) + datos_cifrados
    """
    salt = data[:16]
    iv = data[16:32]
    datos_cifrados = data[32:]
    if len(datos_cifrados) % 16 != 0:
        raise SteganographyException("Los datos cifrados están corruptos o incompletos (no son múltiplo de 16 bytes).")
    key = PBKDF2(password, salt, dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    datos = cipher.decrypt(datos_cifrados)
    # Eliminar relleno PKCS7
    pad_len = datos[-1]
    return datos[:-pad_len]



def cifrar_datos(data, password):
    """
    Cifra los datos usando AES-256 en modo CBC con una contraseña.
    Devuelve: salt (16) + iv (16) + datos_cifrados
    """
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, dkLen=32, count=100_000)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len]) * pad_len
    datos_cifrados = cipher.encrypt(data)
    return salt + iv + datos_cifrados



class SteganographyException(Exception):
    pass

class LSBSteg():
    def __init__(self, im):
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height
        self.maskONEValues = [1,2,4,8,16,32,64,128]
        # Máscara para poner un bit a 1
        self.maskONE = self.maskONEValues.pop(0)
        self.maskZEROValues = [254,253,251,247,239,223,191,127]
        # Máscara para poner un bit a 0
        self.maskZERO = self.maskZEROValues.pop(0)

    def encode_binary(self, files_data):
        """
        Oculta múltiples archivos en la imagen.
        files_data: Lista de tuplas (filename, data)
        """
        if len(files_data) > 255:
            raise SteganographyException("Demasiados archivos (máx 255).")
            
        # Header: [1 byte num_files]
        payload = bytes([len(files_data)])
        
        for filename, data in files_data:
            if isinstance(filename, str):
                filename_bytes = filename.encode('utf-8')
            else:
                filename_bytes = filename
            if len(filename_bytes) > 255:
                raise SteganographyException(f"Nombre de archivo demasiado largo: {filename}")
            
            # Sub-payload: [1 byte name_len] + [name] + [4 bytes data_len] + [data]
            payload += bytes([len(filename_bytes)]) + filename_bytes + struct.pack(">I", len(data)) + data
            
        flat_img = self.image.flatten()
        if len(payload) * 8 > len(flat_img):
            raise SteganographyException(f"Capacidad superada. Se requiere {len(payload)*8} bits, pero la imagen solo tiene {len(flat_img)}.")
            
        for i in range(len(payload) * 8):
            byte_idx = i // 8
            bit_idx = 7 - (i % 8)
            bit = (payload[byte_idx] >> bit_idx) & 1
            flat_img[i] = (flat_img[i] & 0xFE) | bit
            
        return flat_img.reshape(self.image.shape)

    def decode_binary(self):
        """Extrae todos los archivos ocultos en la imagen."""
        flat_img = self.image.flatten()
        total_bits = len(flat_img)
        
        if total_bits < 8: return []
        
        # 1. Leer número de archivos
        num_files = 0
        for i in range(8):
            num_files = (num_files << 1) | (int(flat_img[i]) & 1)
            
        results = []
        current_bit = 8
        
        for _ in range(num_files):
            # 2. Leer name_len
            if current_bit + 8 > total_bits: break
            name_len = 0
            for i in range(8):
                name_len = (name_len << 1) | (int(flat_img[current_bit+i]) & 1)
            current_bit += 8
            
            # 3. Leer nombre
            if current_bit + name_len*8 > total_bits: break
            name_bytes = bytearray()
            for j in range(name_len):
                b = 0
                for k in range(8):
                    b = (b << 1) | (int(flat_img[current_bit + j*8 + k]) & 1)
                name_bytes.append(b)
            filename = name_bytes.decode('utf-8', errors='replace')
            current_bit += name_len * 8
            
            # 4. Leer data_len
            if current_bit + 32 > total_bits: break
            size_bytes = bytearray()
            for i in range(4):
                b = 0
                for k in range(8):
                    b = (b << 1) | (int(flat_img[current_bit + i*8 + k]) & 1)
                size_bytes.append(b)
            data_len = struct.unpack(">I", size_bytes)[0]
            current_bit += 32
            
            # 5. Leer data
            if current_bit + data_len*8 > total_bits: break
            data = bytearray()
            for i in range(data_len):
                b = 0
                for k in range(8):
                    b = (b << 1) | (int(flat_img[current_bit + i*8 + k]) & 1)
                data.append(b)
            current_bit += data_len * 8
            
            results.append((filename, bytes(data)))
            
        return results

# FUNCIONES PARA OCULTAR Y EXTRAER DATOS EN AUDIO
############################################################
def ocultar_datos_en_audio(audio_path, archivo_a_ocultar, salida_path, password=None):
    """Wrapper estandarizado: (portador, ocultar, salida, password)."""
    return ocultar_archivo_en_audio(audio_path, archivo_a_ocultar, salida_path, password)

def extraer_datos_de_audio(audio_path, password=None, ruta_salida=None):
    """Wrapper para extraer un archivo oculto en audio usando la función de alto nivel."""
    return extraer_archivo_de_audio(audio_path, password, ruta_salida)

############################################################
# FUNCIONES PARA OCULTAR Y EXTRAER DATOS EN VIDEO
############################################################
def ocultar_datos_en_video(video_path, archivo_a_ocultar, salida_path, password=None):
    """Wrapper estandarizado: (portador, ocultar, salida, password)."""
    return ocultar_archivo_en_video(video_path, archivo_a_ocultar, salida_path, password)

def extraer_datos_de_video(video_path, password=None, ruta_salida=None):
    """Wrapper para extraer un archivo oculto en video usando la función de alto nivel."""
    return extraer_archivo_de_video(video_path, password, ruta_salida)

# --- FUNCIONES DE ALTO NIVEL PARA AUDIO Y VIDEO (para consistencia de API) ---
def ocultar_audio_en_audio(audio_portador, archivo_a_ocultar, salida_path, password=None):
    """Oculta un archivo en un audio (alias para compatibilidad)."""
    return ocultar_archivo_en_audio(audio_portador, archivo_a_ocultar, salida_path, password)

def extraer_audio_de_audio(audio_portador, password=None, ruta_salida=None):
    """Extrae un archivo oculto en un audio (alias para compatibilidad)."""
    return extraer_archivo_de_audio(audio_portador, password, ruta_salida)

def ocultar_video_en_video(video_portador, archivo_a_ocultar, salida_path, password=None):
    """Oculta un archivo en un video (alias para compatibilidad)."""
    return ocultar_archivo_en_video(video_portador, archivo_a_ocultar, salida_path, password)

def extraer_video_de_video(video_portador, password=None, ruta_salida=None):
    """Extrae un archivo oculto en un video (alias para compatibilidad)."""
    return extraer_archivo_de_video(video_portador, password, ruta_salida)

def es_dato_cifrado(data):
    """
    Verifica si los datos tienen la estructura de cifrado esperada: salt (16) + iv (16) + datos_cifrados (>=16 y múltiplo de 16)
    """
    if not isinstance(data, (bytes, bytearray)):
        return False
    if len(data) < 48:
        return False
    if (len(data) - 32) % 16 != 0:
        return False
    return True
