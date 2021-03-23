import re

"""Filtrado de ayuda

Módulo para detectar mensajes en los que
el usuario está solicitando ayuda.
"""

# Diccionario que será utilizado adelante
help_keywords = [
    ("error", 23), ("pueden", 23), ("puedes", 23),
    ("puedan", 23), ("necesito", 23), ("podria", 23),
    ("algun", 23), ("alguien", 23), ("me", 23),
    ("pido", 23), ("ocupo", 23), ("necesito", 23)
]

# Primer filtro, para ahorrar recursos, sólo indica si el mensaje pudiera 
# contener la palabra "ayuda".
def needs_help(message):
    if re.search("ayud", message):
        return True
    return False

def confirm_help(message):
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

    for pattern, extend in help_keywords:
        if is_close_match(pattern, message, extend):
            return True

    return False
