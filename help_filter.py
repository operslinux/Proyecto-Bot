from utils import remove_accents
import json
import re

"""
La idea es usar este programa como módulo para filtrar
cuidadosamente los mensajes en los que los usuarios piden ayuda.

Cuando se implemente como filtro en el bot, se modificará la
función "main", por ahora es sólo para calibrar el mecanismo de
filtrado.

Pronto se le añadirá un filtro para obtener palabras clave de los mensajes
para tener información más detallada de lo que el usuario necesita y tomar
las acciones necesarias.
"""


# Función para remover los acentos
def remove_accents(text):
    for key, value in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}.items(): text = text.replace(key, value)
    return text


# Diccionario que será utilizado adelante
help_keywords = [
    ("error", 23), ("pueden", 23), ("puedes", 23),
    ("puedan", 23), ("necesito", 23), ("podria", 23),
    ("algun", 23), ("alguien", 23), ("me", 23),
    ("pido", 23), ("ocupo", 23), ("necesito", 23)
]


def needs_help(message):
    # Verifica que las palabras clave (patrones) estén a una distancia razonable.
    def is_close_match(pattern, text, extend):
        matches = re.finditer(pattern, text)
        for match in matches:
            if match is not None:
                # Verificar si 'ayuda' y la palabra clave están presentes
                # en lo que abarca la 'distancia razonable' (extend).
                start = match.start()
                text = message[start: start + extend]
                if re.search("ayud", text): return True
            return False

    for keyword_tuple in help_keywords:
        pattern, extend = keyword_tuple
        if is_close_match(pattern, message, extend):
            return True
    return False


def main():
    # Cargar chat exportado.
    with open("result.json", "r") as file:
        chat_history = json.load(file)
        file.close()
    chat = chat_history["messages"]

    # Filtrar los mensajes que no contienen enlaces, remover los acentos y convertirlos a minúsculas.
    # Filtrar los mensajes que contienen "ayuda" en alguna parte.
    # Filtrar los mensajes que dan indicios de REQUERIR ayuda.

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓                 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓                 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    clear_messages = [remove_accents(item["text"].lower()) for item in chat if type(item["text"]) == str]
    filter_help = [item for item in clear_messages if re.search("ayuda", item)]
    confirm_help = [message for message in filter_help if needs_help(message)]

    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑                 ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑                 ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    # Convertirlos en sets para verificar que se filtraron correctamente.
    confirmed_help_messages = set(confirm_help)
    not_filtred_help_messages = set(filter_help)
    ignored_help_messages = confirmed_help_messages ^ not_filtred_help_messages

    # Imprimir mensajes en los que se requiere ayuda.
    for index, message in enumerate(confirmed_help_messages):
        print(f"\n{message}\n\n{'. ' * 30} #{index} MENSAJE CONFIRMADO {'. ' * 30}\n")

    # Imprimir mensajes ignorados
    """for index, message in enumerate(ignored_help_messages)  : 
    print(f"\n{message}\n\n{'. '*30} #{index} MENSAJE IGNORADO {'. '*30}\n") """


if __name__ == "__main__":
    main()
