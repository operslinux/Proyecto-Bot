import re
import pickle
from utils import KaliTools

KaliTools = KaliTools()

with open("help_messages.pick", "rb") as file:
    data=file.read()
    file.close()
messages=pickle.loads(data)

# Lista de software instalable para ser detectado.
all_installables = []
tools = [ tool.lower() for tool in KaliTools.tools_list ]
all_installables.extend(tools)
all_installables.extend(["ubuntu", "windows", "kali", "fedora", "parrot"])

# Palabras clave para aportar contexto.
keywords = [
"boot", "usb", "pdf", "curso", "maquina virtual",
"payload", "audio", "red", "wifi", "libro", "libros"
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
    installables: si el mensaje puede relacionarse con software instalable, y cuál.
    beginner_tabs: si el mensaje se puede relacionar con un usuario primerizo en busca de recursos.
    keywords: palabras clave para aportar más contexto, y cuáles.
    programming_languages: si el mensaje se puede relacionar con un lenguaje de programación, y cuál.
"""

class TagMessage:
    def __init__(self, message):
        # Elimina los caracteres que no son alfanuméricos
        # y genera una versión del mensaje como lista y otra como cadena de texto.
        matches = re.finditer("\w+", message.lower())
        self.message_list = [ message[match.start():match.end()] for match in matches ]
        self.message = ' '.join(self.message_list)

        # Define etiquetas y los atributos correspondientes.
        self.define_tags()

        # Genera el atributo "all_tags".
        self.define_matches()

    def define_tags(self):
        self.errors = "error" in self.message_list
        self.installation_tags = self.installation_tags()
        self.installables = [ software for software in all_installables if software in self.message_list ]
        self.beginner_tags = self.beginner_tags()
        self.keywords = [ keyword for keyword in keywords if keyword in self.message_list ]
        self.programming_languages = [ language for language in programming_languages if language in self.message_list ]

    def define_matches(self):
        tags = []
        if self.errors: tags.append("error")
        if self.installation_tags: tags.append("installation")
        if self.installables: tags.append("installable")
        if self.beginner_tags: tags.append("beginner")
        if self.keywords: tags.append("keyword")
        if self.programming_languages: tags.append("programming_language")

        if tags:
            self.all_tags = tags
        else:self.all_tags = None

    def installation_tags(self):
        if re.search("instal", self.message) is not None:
            return True
        return False

    def beginner_tags(self):
        if re.search("mundo", self.message) is not None:
            return True
        if re.search("mundillo", self.message) is not None:
            return True
        if re.search("soy nuevo", self.message) is not None:
            return True
        return False
"""
"error"
"installation"
"installable"
"beginner"
"keyword"
"programming_language"
"""
def hierarchy_filter(tags):
    # Ayudará a definir qué etiqueta es más importante
    # la tupla contiene las etiquetas a comparar
    # el valor es la etiqueta que se removerá de la lista de etiquetas
    # ya que la otra es más relevante.
    dic = {
            ("error", "installation"): "error",
            ("error", "installable"): "error",
            ("error", "programming_language"): "error",
            ("error", "beginner"): "error",
            ("error", "keyword"): "error",
            }
    for (x, y), word_to_remove in dic.items():
        # Si las etiquetas de la tupla están presentes en las etiquetas, entonces
        # remover el valor correspondiente de las etiquetas.
        if x in tags and y in tags:
            tags.remove(word_to_remove)

    # Definir la etiqueta principal y las etiquetas adicionales
    dic = {
            ("installation", "installable"): {"main":"installable", "aditional":"installation"},
            ("installation", "programming_language"): {"main":"programming_language", "aditional":"installation"},
            ("installation", "beginner"): {"main":"installation", "aditional":"beginner"},
            ("installable", "beginner"):{"main":"installable", "aditional":"beginner"},
            ("installable", "programming_language"):{"main":"installable","aditional":"programming_language"},
            ("installation", "keyword"):{"main":"keyword","aditional":"installation"},
            ("installable", "keyword"):{"main":"installable", "aditional":"keyword"}
            }
    aditional = []
    ordered = False
    if len(tags) > 1:
        for (x, y), value in dic.items():
            # Si ambas etiquetas (de la tupla) están presentes, definir el órden
            # como se especifica en el valor correspondiente.
            if x in tags and y in tags:
                aditional.append(value["aditional"])
                main = value["main"]
                ordered = True
        if ordered:
            aditional = set(aditional)
            order = {"main":main, "aditional":aditional}
        else:
            order = {"main":[], "aditional":tags}
    else:
        order = {"main":tags, "aditional":[]}

    return tags, order

def define_actions(tagged_message):
    all_tags = tagged_message.all_tags
    # Obtiene una versión filtrada de las etiquetas junto al
    # órden que pueden tener.
    formatted_tags, order = hierarchy_filter(all_tags)
    print()
    print(tagged_message.message)
    print(formatted_tags)
    print(order)
    print("+-"*40)
    print()

for message in messages:
    # Crea el objeto "mesaje etiquetado" con los atributos relacionados
    # con el etiquetado del mensaje.
    tagged_message = TagMessage(message)
    # Si contiene etiquetas, entonces, que se definan las acciones a tomar.
    if tagged_message.all_tags is not None:
        actions = define_actions(tagged_message)

