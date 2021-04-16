from telegram import InlineKeyboardButton, InputMediaDocument
import json
import re
import os

"""Útiles
Módulo con funciones que se implementan
en distintos scripts.
"""

KALI_TOOLS_DATA_PATH = "resources/kali_tools/kali_tools.json"

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
# Se puede arreglar para sólo eliminar ciertos caracteres y otros no.       ##### REVISAR #####
def clean_text(text):
    for key, value in {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u"}.items():
        text = text.replace(key, value)
    text = text.lower()
    matches = re.finditer("\w+", text)
    text_list = [text[match.start():match.end()] for match in matches]
    text = ' '.join(text_list)
    return text


def get_msg_id(update):
    if update.edited_message:
        return update.edited_message.message_id
    if update.message:
        return update.message.message_id
    if update.callback_query:
        return update.callback_query.message.message_id
    return "chat id not found"

def get_id(update):
    if update.edited_message:
        return update.edited_message.chat.id
    if update.message:
        return update.message.chat.id
    if update.callback_query:
        return update.callback_query.message.chat.id
    return "chat id not found"

def sort_by_letter(installables):
    alphabet = [
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
            "k", "l", "m", "n", "ñ", "o", "p", "q", "r", "s", "t",
            "u", "v", "w", "x", "y", "z"
            ]
    return dict([(letter, [item for item in installables if item[0].lower() == letter]) for letter in alphabet])

def make_alphabet_keyboard(lenght, ordered):
    # Lista con todas las letras del alfabeto
    characters = [key for key in ordered.keys()]
    # Dividir la lista en filas de 8 elementos
    chunks = list(range(0, len(characters), lenght))
    rows = [characters[div:div+lenght] for div in chunks]
    # Hacer el teclado alfabético con las filas de letras
    keyboard = [
            [InlineKeyboardButton(letter, callback_data = letter) for letter in row]
            for row in rows
            ]
    keyboard.append([InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")])

    return keyboard

def make_programs_message(programs):
    # Ordenar los programas alfabéticamente
    programs = sorted(programs)
    programs_list = list(enumerate(programs, 1))
    # Dividir los programas en filas de 8 elementos (tuplas).
    chunks = range(0, len(programs_list), 8)
    rows = [programs_list[div:div+8] for div in chunks]
    # Las filas contienen tuplas, los valores de las tuplas contienen
    # los índices y sus respectivos programas (uno es el texto y el otro
    # es la callback_query).
    keyboard = [
            [InlineKeyboardButton(str(tup[0]), callback_data = str(tup[1])) for tup in tuples]
            for tuples in rows
            ]
    # Botones adicionales.
    keyboard.append([InlineKeyboardButton("Seleccionar otra inicial", callback_data = "Seleccionar otra inicial")])
    keyboard.append([InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")])
    # Texto del mensaje, conteniendo los programas con sus respectivos índices.
    text = ''.join([f"{idx}.- {program}\n" for idx, program in enumerate(programs, 1)])
    return text, keyboard

def get_file_chunks(files, leng):
    files = [InputMediaDocument(file_id) for file_id in files]
    idxs = list(range(0, len(files), leng))
    chunks = [files[chunk:chunk+leng] for chunk in idxs]
    return chunks

with open("resources/installables.json", "r") as file:
    installables_database = json.load(file)
    file.close()

with open("resources/custom_contents.json", "r") as file:
    customs_database = json.load(file)
    file.close()

def reload_customs_database():
    data = json.dumps(customs_database, indent = 4, ensure_ascii = False)
    with open("resources/custom_contents.json", "w") as file:
        file.write(data)
        file.close()

def get_installable_post_id(installable):
    return installables_database[installable]["post_id"]

def reload_database():
    data = json.dumps(installables_database, indent = 4, ensure_ascii = False)
    with open("resources/installables.json", "w") as file:
        file.write(data)
        file.close()

def register_to_installables(data):
    installable = data["installable"]
    title = data["title"]
    keywords = data["keywords"]
    urls = data["urls"]
    files = data["files"]
    post_id = data["post_id"]
    description = data["description"]
    if installable in keywords:
        keywords.remove(installable)
    if installable.lower() in keywords:
        keywords.remove(installable.lower())

    installables_database[installable]["custom"][title]= {
            "description":description,
            "keywords":keywords,
            "post_id":post_id,
            "urls":urls,
            "files":files
            }
    reload_database()

def has_installable(title, desc, keywords):
    def get_words(text):
        list1 = text.split(" ")
        matches = re.finditer("\w+", text.lower())
        list2 = [text[match.start():match.end()] for match in matches]
        list1.extend(list2)
        result = set([item.lower() for item in list1])
        return result
    all_ = get_words(title).union(get_words(desc))
    all_ = all_.union(set([item.lower() for item in keywords]))
    installables = dict([(i.lower(), i) for i in installables_database.keys()])
    found = dict([(installables[item], installables_database[installables[item]]["post_id"]) for item in all_ if item in installables])

    return found

def is_installable(item):
    return item in installables_database

def register_installable_to_database(name, data):
    installables_database[name] = data
    reload_database()

def register_custom_to_database(name, data):
    customs_database[name] = data
    reload_customs_database()
