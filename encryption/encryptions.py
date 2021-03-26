from base64 import b64encode, b64decode
from getpass import getpass
import tarfile
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2

"""
Este script se encarga del cifrado y descifrado de archivos/directorios
con llave simétrica implementando el algoritmo AES cbc.
La contraseña debe ser compartida previamente con los colaboradores.
"""

salt=bytes('\xbc\x9b\xb5.\xc0\xee~\r\xab\xd1\xdd\xcbh\x91\xb4g'.encode("utf-8"))

class Encrypt:
    def __init__(self, input_file):
        print("Encriptar...")
        password = getpass(prompt = "Inserta la contraseña: ")
        # Genera una llave de 32 bytes con el salt y la contraseña
        # la contraseña debería ser generada de manera aleatoria, yo
        # implementé una de 32 bytes codificada a base 64.
        key = PBKDF2(password, salt, dkLen = 32)
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        iv = b64encode(iv)
        # Escribir el vector de inicialización y una nueva línea.
        output_file = open(f"{input_file}.safe", "wb")
        output_file.write(iv + b"\n")
        # Comprimir el archivo o el contenido de un directorio,
        # regresa los bytes del archivo comprimido.
        data = self.tar_bytes(input_file)
        encrypted_data = b64encode(cipher.encrypt(pad(data, AES.block_size)))
        # Escribir la información encriptada y codificada en base 64.
        output_file.write(encrypted_data)
        output_file.close()

    def tar_bytes(self, input_file):
        # Comprime el archivo o la carpeta requerido
        filename = os.path.basename(input_file)
        if os.path.isdir(input_file):
            tar = tarfile.open(".delete_this_tar.tar.gz", "w:gz")
            tar.add(input_file, filename)
            tar.close()
        elif os.path.isfile(input_file):
            tar = tarfile.open(".delete_this_tar.tar.gz", "w:gz")
            tar.add(input_file, filename, True)
            tar.close()

        # Regresar la información del archivo para ser cifrada.
        file = open(".delete_this_tar.tar.gz", "rb")
        file_bytes = file.read()
        file.close()
        os.remove(".delete_this_tar.tar.gz")
        return file_bytes

class Decrypt:
    def __init__(self, input_file):
        print("Desencriptar...")
        password=getpass(prompt = "Inserta la contraseña: ")
        # Genera la llave con la contraseña y el salt, debería ser
        # la misma llave si la contraseña y el salt son los mismos
        # usados al momento del cifrado.
        key = PBKDF2(password, salt, dkLen = 32)
        input_file = open(input_file, "rb")
        # Lee y decodifica el vector de inicialización y la información encriptada.
        iv, encrypted_data = (b64decode(line) for line in input_file.readlines())
        input_file.close()
        cipher = AES.new(key, AES.MODE_CBC, iv = iv)
        # Intenta desencriptar la información, si la llave no es la correcta, el script
        # se detendrá.
        try:
            original_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        except:
            print("La contraseña es incorrecta.")
            input("Presiona Enter para salir.")
            exit()
        # Si la llave es la correcta, escribirá los bytes descifrados
        compressed_file = open(".delete_this_tar", "wb")
        compressed_file.write(original_data)
        compressed_file.close()
        # Descomprime y elimina el archivo.
        tar = tarfile.open(".delete_this_tar")
        tar.extractall(os.getcwd())
        tar.close()
        os.remove(".delete_this_tar")

