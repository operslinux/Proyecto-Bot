import re
from python_modules.utils import KaliTools

KaliTools = KaliTools()

# Lista de software instalable para ser detectado.
all_installables = []
tools = [ tool.lower() for tool in KaliTools.tools_list ]
all_installables.extend(tools)
all_installables.extend([
    "ubuntu", "windows", "kali", "fedora", "parrot", "mint",
    ])

# Palabras clave para aportar contexto.
general_keywords = [
    "boot", "usb", "pdf", "curso", "maquina virtual",
    "payload", "audio", "red", "wifi", "libro", "libros",
    "mac", "gpg", "adaptador", "particion", "raspberry",
    "iso", "quiero aprender", "exploit", "virtual box"
]

# Palabras que suelen usar los novatos.
beginner_keywords = ["mundo", "mundillo", "soy nuevo"]

# Lenguajes de programación incluídos para detectar.
programming_languages = [
    "python", "c++", "visual basic", "c#",
    "javascript", "java script", "php", "sql", "ruby", "shell",
    "type script", "typescript", "java", "bash", "c"
]


class TagMessage:
    """Contiene los atributos del etiquetado de los mensajes, que son:

    all_tags: lista de todas las etiquetas encontradas.
    errors: si el mensaje puede relacionarse con un error.
    installation_tags: si el mensaje puede relacionarse con una instalación.
    installables: si el mensaje puede relacionarse con software instalable, y cuál.
    beginner_tabs: si el mensaje se puede relacionar con un usuario primerizo en busca de recursos.
    keywords: palabras clave para aportar más contexto, y cuáles.
    programming_languages: si el mensaje se puede relacionar con un lenguaje de programación, y cuál.

    la función "from_tag" está para obtener atributos a partir de las etiquetas del atributo "all_tags".
    """
    def __init__(self, message):
        # Elimina los caracteres que no son alfanuméricos
        # y genera una versión del mensaje como lista y otra como cadena de texto.
        matches = re.finditer("\w+", message.lower())
        self.message_list = [message[match.start():match.end()] for match in matches]
        self.message = ' '.join(self.message_list)

        # Define etiquetas y los atributos correspondientes.

        self.errors = "error" in self.message_list
        # Busca indicios de palabras derivadas de "instalación", "instalar", etc.
        self.installation_tags = re.search("instal", self.message) is not None
        # Identifica software instalable, de la lista "all_installables"
        self.installables = [software for software in all_installables if software in self.message_list]
        # Detecta indicios de que el usuario diga ser novato (ver lista beginner_keywords).
        self.beginner_tags = any([True for kwd in beginner_keywords if re.search(kwd, self.message)])
        # Detecta palabras clave.
        self.keywords = [keyword for keyword in general_keywords if keyword in self.message_list]
        # Detecta si se menciona un lenguaje de programación.
        self.programming_languages = [language for language in programming_languages if language in self.message_list]

        self.tags_dict = {
                "error":self.errors, "installation":self.installation_tags,
                "installable":self.installables, "beginner":self.beginner_tags,
                "keyword":self.keywords, "programming_language":self.programming_languages
                }

        self.all_tags = [attr for attr in self.tags_dict if self.tags_dict[attr]]

    def from_tag(self, tag):
        return self.tags_dict[tag]


def hierarchy_filter(tags):
    """Filtro jerárquico
    Ayudará a definir qué etiqueta es más importante
    la tupla contiene las etiquetas a comparar
    el valor es la etiqueta que se removerá de la lista de etiquetas
    ya que la otra es más relevante.
     """
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
    message_text = tagged_message.message
    # Obtiene una versión filtrada de las etiquetas junto al
    # órden que pueden tener.
    formatted_tags, order = hierarchy_filter(all_tags)

    # Tratar de calcular la precisión de las etiquetas dependiendo de
    # la objetividad de las mismas y el largo del mensaje.
    accuracy_dict = {
            "keyword":60, "programming_language":100, "beginner":50,
            "installable":90, "installation":50, "error":100
    }
    # Precisión promedio de las etiquetas
    tags_accuracy = sum([accuracy_dict[tag] for tag in formatted_tags])/len(formatted_tags)
    #print(tags_accuracy)

    total = len(formatted_tags) * tags_accuracy
    partial = len(message_text) / 35
    accuracy = total / partial
    print(tagged_message.message)
    if accuracy > 50 and len(formatted_tags) > 2:
        print("Te diré cómo hacerlo!")
    elif accuracy > 50:
        print("Quizá esto podría servirte...")
    elif accuracy < 50 and accuracy > 30:
        print("Quizá esto podría servirte...")
    elif accuracy <= 30:
        print("No sé cómo ayudarte, pero mira esto...")

    for tag in formatted_tags:
        print(tag, "→ → →", tagged_message.from_tag(tag))
    print(f"Accuracy → → → {int(accuracy)}%")
    print("+-"*40)
    actions = [
            "link to tagged resources", "beginner introduction", "show all resourses (pfd, course)",
            "ask for context", "send specific answer(depending on context)", ""
            ]

"""
"error": errors (bool)
"installation": installation_tags (list)
"installable": installables (list)
"beginner": beginner_tabs (bool)
"keyword": keywords (list)
"programming_language": programming_languages (list)
"""

def process_message_tags(message):
    # Crea el objeto "mesaje etiquetado" con los atributos relacionados
    # con el etiquetado del mensaje.
    tagged_message = TagMessage(message)
    # Si contiene etiquetas, entonces, que se definan las acciones a tomar.
    if tagged_message.all_tags:
        actions = define_actions(tagged_message)

