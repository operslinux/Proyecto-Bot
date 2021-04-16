from telegram.ext import MessageFilter
from help_filter import needs_help, confirm_help
from process_help import Recolector

"""
Este módulo puede ser implementado para filtrar y procesar mensajes,
se arreglará su disposición cuando el módulo del filtro de ayuda
esté listo.
"""

class HelpHandler(MessageFilter):
    def filter(self, message):
        return needs_help(str(message.text).lower()) and confirm_help(str(message.text).lower())

################################## PRUEBAS ################################
if __name__ == "__main__":
    import json
    # Cargar chat exportado.
    with open("result.json", "r") as file:
        chat_history = json.load(file)
        file.close()
    chat = chat_history["messages"]
    messages = [item["text"] for item in chat if isinstance((item["text"]), str)]

    # Probar la recolección de información
    for message in messages:
        # Si se detecta y confirma el requerimiento
        # de ayuda en el mensaje, recolectar recursos.
        if needs_help(message) and confirm_help(message):
            item = Recolector(message.lower())
            if any((
                    item.data["installables"],
                    item.data["installation"],
                    item.data["installable_keywords"],
                    item.data["custom_from_keywords"],
                    )):
                data = json.dumps(item.data, indent = 2, ensure_ascii = False)
                print(message)
                print(data)
                print("+-"*40)
