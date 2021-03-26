import os
import sys
from re import search
from requests.utils import unquote
from time import sleep
from encryptions import Encrypt, Decrypt

"""
Este script sólo define el contenido a encriptar/desencriptar
y el módulo importado "encryptions.py" procede con la tarea requerida.
"""

def get_path(link):
    match = search("file://", link)
    if match:
        idx = match.end()
        # Regresa la ruta sin "file://" y decodificada a utf-8
        return unquote(link[idx:])
    else:
        return False

def main():
    # Los argumentos que vienen del archivo .desktop.
    # Éstos incluyen "encrypt" o "decrypt" respectivamente y la ruta del archivo
    # "percent-encoded".
    encryption_mode = sys.argv[1]
    if len(sys.argv) > 1:
        # Se obtiene una ruta normal de la ruta codificada
        file_to_process = get_path(sys.argv[2])
        if file_to_process:
            # Hace la tarea requerida en el argumento No. 1
            if encryption_mode == "encrypt":
                Encrypt(os.path.realpath(file_to_process))
            elif encryption_mode == "decrypt":
                Decrypt(os.path.realpath(file_to_process))
        else:
            print("Tienes que arrastrar el archivo para encriptarlo/desencriptarlo.")
            sleep(8)

if __name__ == "__main__":
    main()
