import re
import pickle
from utils import KaliTools

KaliTools = KaliTools()

with open("help_messages.pick", "rb") as file:
    data=file.read()
    file.close()
messages=pickle.loads(data)

all_tools = [ tool.lower() for tool in KaliTools.tools_list ]

# Palabras clave para aportar contexto.
keywords = [
"boot", "usb", "pdf", "curso", "maquina virtual",
"payload", "audio", "red", "wifi"
]

# Lenguajes de programación incluídos para detectar.
programming_languages = [
"python", "c++", "visual basic", "c#",
"javascript", "java script", "php", "sql", "ruby", "shell",
"type script", "typescript", "java", "bash"
]

"""
Esta clase contiene los atributos del etiquetado de los mensajes, que son:

    all_tags: lista de todas las etiquetas encontradas, None si no se encontraron.

    errors: si el mensaje puede relacionarse con un error.
    installation_tags: si el mensaje puede relacionarse con una instalación.
    programs: si el mensaje puede relacionarse con un programa, y cuál.
    begginer_tabs: si el mensaje se puede relacionar con un usuario primerizo en busca de recursos.
    keywords: palabras clave para aportar más contexto.
    programming_languages: si el mensaje se puede relacionar con un lenguaje de programación, y cuál.
"""

class TagMessage:
    def __init__(self, message):
        # Elimina los caracteres que no son alfanuméricos
        # y genera una versión del mensaje como lista y otra como cadena de texto.
        matches = re.finditer("\w+", message.lower())
        self.message_list = [ message[match.start():match.end()] for match in matches ]
        self.message = ' '.join(x for x in self.message_list)

        # Define etiquetas y los atributos correspondientes.
        self.define_tags()

        # Genera el atributo "all_tags".
        self.define_matches()

    def define_tags(self):
        self.errors = "error" in self.message_list
        self.installation_tags = self.installation_tags()
        self.programs = [ tool for tool in all_tools if tool in self.message_list ]
        self.begginer_tags = self.begginer_tags()
        self.keywords = [ keyword for keyword in keywords if keyword in self.message_list ]
        self.programming_languages = [ language for language in programming_languages if language in self.message_list ]

    def define_matches(self):
        tags = []
        if self.errors: tags.append("error")
        if self.installation_tags: tags.append("installation")
        if len(self.programs) > 0: tags.append("program")
        if self.begginer_tags: tags.append("begginer")
        if len(self.keywords) > 0: tags.append("keyword")
        if len(self.programming_languages) > 0: tags.append("programming_language")

        if len(tags) > 0:
            self.all_tags = tags
        else:self.all_tags = None

    def installation_tags(self):
        if re.search("instal", self.message) is not None:
            return True
        return False

    def begginer_tags(self):
        if re.search("mundo", self.message) is not None:
            return True
        if re.search("soy nuevo", self.message) is not None:
            return True
        return False

for message in messages:
    tagged_message = TagMessage(message)
    print(tagged_message.all_tags)

