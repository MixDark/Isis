import cv2
import numpy as np
from colorama import init, Fore, Style
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os
import pwinput
import shutil

# Inicializar colorama
init(autoreset=True)

# --- Funciones de cifrado y descifrado AES ---
def cifrar_datos(data, password):
    """
    Cifra los datos usando AES-256 en modo CBC con una contraseña.
    Devuelve: salt + iv + datos_cifrados
    """
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, dkLen=32, count=100_000)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # Relleno PKCS7
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len]) * pad_len
    datos_cifrados = cipher.encrypt(data)
    return salt + iv + datos_cifrados

def descifrar_datos(data, password):
    """
    Descifra los datos usando AES-256 en modo CBC con una contraseña.
    Espera: salt (16) + iv (16) + datos_cifrados
    """
    salt = data[:16]
    iv = data[16:32]
    datos_cifrados = data[32:]
    key = PBKDF2(password, salt, dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    datos = cipher.decrypt(datos_cifrados)
    # Eliminar relleno PKCS7
    pad_len = datos[-1]
    return datos[:-pad_len]


def banner():
    ancho = shutil.get_terminal_size((80, 20)).columns
    ascii_art = """
▄█    ▄▄▄▄▄   ▄█    ▄▄▄▄▄  
██   █     ▀▄ ██   █     ▀▄
██ ▄  ▀▀▀▀▄   ██ ▄  ▀▀▀▀▄  
▐█  ▀▄▄▄▄▀    ▐█  ▀▄▄▄▄▀   
 ▐             ▐           
"""
    for linea in ascii_art.splitlines():
        print(Fore.GREEN + Style.BRIGHT + linea.center(ancho))
    print()
    print(Fore.GREEN + Style.BRIGHT + "Isis - Esteganografía avanzada".center(ancho))
    print(Fore.GREEN + "https://github.com/MixDark".center(ancho))
    print(Fore.GREEN + "Creado por Mix Dark".center(ancho))
    print(Fore.GREEN + "Fecha: 24/07/2025".center(ancho))
    print(Fore.GREEN + "Version: 1.0".center(ancho))
    print("\n\n")

def menu():
    print(Fore.CYAN + "1. Ocultar archivo")
    print(Fore.CYAN + "2. Extraer archivo")
    print(Fore.CYAN + "3. Salir\n")
    opcion = input(Fore.GREEN + "Seleccione una opción (1-3): ")
    return opcion

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
        self.curwidth = 0  # Posición actual en ancho
        self.curheight = 0 # Posición actual en alto
        self.curchan = 0   # Canal actual

    def put_binary_value(self, bits):
        # Inserta los bits en la imagen
        for c in bits:
            val = list(self.image[self.curheight,self.curwidth])
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO
            self.image[self.curheight,self.curwidth] = tuple(val)
            self.next_slot()
    def next_slot(self):
        # Avanza al siguiente canal/píxel
        if self.curchan == self.nbchannels-1:
            self.curchan = 0
            if self.curwidth == self.width-1:
                self.curwidth = 0
                if self.curheight == self.height-1:
                    self.curheight = 0
                    if self.maskONE == 128:
                        raise SteganographyException("No hay más espacio disponible (imagen llena)")
                    else:
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight +=1
            else:
                self.curwidth +=1
        else:
            self.curchan +=1
    def read_bit(self):
        # Lee un bit de la imagen
        val = self.image[self.curheight,self.curwidth][self.curchan]
        val = int(val) & self.maskONE
        self.next_slot()
        if val > 0:
            return "1"
        else:
            return "0"
    def read_byte(self):
        return self.read_bits(8)
    def read_bits(self, nb):
        # Lee nb bits de la imagen
        bits = ""
        for i in range(nb):
            bits += self.read_bit()
        return bits
    def byteValue(self, val):
        return self.binary_value(val, 8)
    def binary_value(self, val, bitsize):
        # Devuelve el valor binario de un entero como string de bitsize bits
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException("\nEl valor binario es mayor al tamaño esperado\n")
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval
    def encode_binary(self, data, filename=None):
        # Guarda el nombre del archivo antes de los datos
        if filename is None:
            filename = "extraido.bin"
        filename_bytes = filename.encode('utf-8')
        filename_len = len(filename_bytes)
        if filename_len > 255:
            raise SteganographyException("\nEl nombre del archivo es demasiado largo (máx 255 caracteres)\n")
        # Guarda longitud del nombre en 1 byte
        self.put_binary_value(self.binary_value(filename_len, 8))
        # Guarda el nombre del archivo
        for b in filename_bytes:
            self.put_binary_value(self.byteValue(b))
        # Guarda la longitud de los datos en 8 bytes (64 bits)
        l = len(data)
        if self.width*self.height*self.nbchannels < l+64+filename_len+8:
            raise SteganographyException("\nLa imagen portadora no es lo suficientemente grande para ocultar todos los datos\n")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            byte = byte if isinstance(byte, int) else ord(byte)
            self.put_binary_value(self.byteValue(byte))
        return self.image
    def decode_binary(self):
        # Lee la longitud del nombre (1 byte)
        filename_len = int(self.read_bits(8), 2)
        # Lee el nombre del archivo
        filename_bytes = bytearray()
        for _ in range(filename_len):
            filename_bytes.append(int(self.read_byte(), 2))
        filename = filename_bytes.decode('utf-8', errors='replace')
        # Lee la longitud de los datos (8 bytes)
        l = int(self.read_bits(64), 2)
        output = b""
        for i in range(l):
            output += bytearray([int(self.read_byte(),2)])
        return filename, output
    def decode_image(self):
        width = int(self.read_bits(16),2)
        height = int(self.read_bits(16),2)
        # Crea una imagen vacía para los datos extraídos
        unhideimg = np.zeros((height, width, 3), np.uint8)
        for h in range(height):
            for w in range(width):
                for chan in range(3):
                    val = list(unhideimg[h,w])
                    val[chan] = int(self.read_byte(),2)
                    unhideimg[h,w] = tuple(val)
        return unhideimg


# --- Función para ocultar archivo ---
def ocultar_archivo():
    lossy_formats = ["jpeg", "jpg"]
    in_f = input(Fore.CYAN + "Ingrese la ruta de la imagen portadora: ")
    out_f = input(Fore.CYAN + "Ingrese la ruta de la imagen de salida: ")
    file_to_hide = input(Fore.CYAN + "Ingrese la ruta del archivo a ocultar: ")
    usar_contraseña = input(Fore.CYAN + "¿Desea proteger el archivo con contraseña? (s/n): ").strip().lower() == 's'
    contraseña = None
    if usar_contraseña:
        contraseña = pwinput.pwinput(Fore.CYAN + "Ingrese la contraseña: ", mask='*')
    in_img = cv2.imread(in_f)
    if in_img is None:
        print(Fore.RED + "\nNo se pudo abrir la imagen portadora.\n")
        return
    steg = LSBSteg(in_img)
    out_name, out_ext = out_f.rsplit(".", 1)
    if out_ext.lower() in lossy_formats:
        out_f = out_name + ".png"
        print(Fore.YELLOW + "\nEl archivo de salida se cambió a ", out_f)
    if not out_f.lower().endswith('.png'):
        print(Fore.RED + "\nADVERTENCIA: La imagen de salida debe ser PNG para evitar pérdida de datos.\n")
    try:
        data = open(file_to_hide, "rb").read()
        nombre_archivo = os.path.basename(file_to_hide)
        if usar_contraseña:
            data = cifrar_datos(data, contraseña)
        if len(data) > in_img.size:
            print(Fore.RED + "\nEl archivo a ocultar es demasiado grande para la imagen portadora.\n")
            return
        res = steg.encode_binary(data, filename=nombre_archivo)
        cv2.imwrite(out_f, res)
        print(Fore.GREEN + f"\nArchivo ocultado exitosamente.\n")
    except Exception as e:
        print(Fore.RED + f"\nError durante el procesamiento: {e}\n")

# --- Función para extraer archivo ---
def extraer_archivo():
    in_f = input(Fore.CYAN + "Ingrese la ruta de la imagen con el archivo oculto: ")
    usar_contraseña = input(Fore.CYAN + "¿El archivo está protegido con contraseña? (s/n): ").strip().lower() == 's'
    contraseña = None
    if usar_contraseña:
        contraseña = pwinput.pwinput(Fore.CYAN + "Ingrese la contraseña: ", mask='*')
    if not in_f.lower().endswith('.png'):
        print(Fore.RED + "\nADVERTENCIA: La imagen debe ser PNG. Si usas JPG u otro formato, los datos pueden estar corruptos.\n")
    in_img = cv2.imread(in_f)
    if in_img is None:
        print(Fore.RED + "\nNo se pudo abrir la imagen.\n")
        return
    steg = LSBSteg(in_img)
    try:
        filename, raw = steg.decode_binary()
        if not raw:
            print(Fore.RED + "\nNo se pudo extraer ningún dato. ¿Seguro que la imagen tiene datos ocultos?\n")
            return
        if usar_contraseña:
            try:
                raw = descifrar_datos(raw, contraseña)
            except Exception:
                print(Fore.RED + "\nContraseña incorrecta o datos corruptos. No se pudo descifrar el archivo.\n")
                return
        carpeta = os.path.dirname(in_f)
        ruta_salida = os.path.join(carpeta, filename)
        with open(ruta_salida, "wb") as f:
            f.write(raw)
        print(Fore.GREEN + f"\nArchivo extraído exitosamente\n")
    except Exception as e:
        print(Fore.RED + f"\nError durante la extracción: {e}\n")


def main():
    banner()
    while True:
        opcion = menu()
        if opcion == "1":
            ocultar_archivo()
        elif opcion == "2":
            extraer_archivo()
        elif opcion == "3":
            print(Fore.CYAN + "\n¡Hasta luego!")
            break
        else:
            print(Fore.RED + "\nOpción no válida. Intente de nuevo.\n")

if __name__=="__main__":
    main()
