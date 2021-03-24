import json
import re
import os

"""Útiles
Módulo con funciones que se implementan
en distintos scripts.
"""

KALI_TOOLS_DATA_PATH = "python_modules/kali_tools/kali_tools.json"

# Esta clase nos permite obtener las herramientas en diferentes formatos.
class KaliTools:
    def __init__(self):
        with open(KALI_TOOLS_DATA_PATH, "r") as file:
            # Base de datos, su estructura está definida en /kali_tools/LEEME.txt
            self.database = json.load(file)
            file.close()

        # Lista de todas las herramienas.
        self.tools_list = [tool for category in self.database for tool in self.database[category]]

        # Una lista de las categorías.
        self.categories_list = [category for category in self.database]

        # Diccionario de herramientas, las llaves son las herramientas, los valores son el contenido de la herramienta.
        self.tools_dictionary = dict([(tool, self.database[category][tool]) for category in self.database for tool in self.database[category]])

        # Diccionario de categorías, sólo las categorias con sus respectivas herramientas.
        self.category_tools = dict([(category, list(self.database[category].keys())) for category in self.database])


# Función para limpiar el mensaje, con eso nos referimos a remover
# los acentos, los signos de puntuación y las mayúsculas.
def clean_text(text):
    for key, value in {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u"}.items():
        text = text.replace(key, value)
    text = text.lower()
    matches = re.finditer("\w+", text)
    text_list = [text[match.start():match.end()] for match in matches]
    text = ' '.join(text_list)
    return text


