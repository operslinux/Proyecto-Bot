from help_filter import needs_help, confirm_help
from utils import clean_text
from process_help import Recolector

############################################# PRUEBAS ################################
import json
# Cargar chat exportado.
with open("result.json", "r") as file:
    chat_history = json.load(file)
    file.close()
chat = chat_history["messages"]
messages = [item["text"] for item in chat if isinstance((item["text"]), str)]

# Probar la recolección de información
for message in messages:
    if needs_help(message) and confirm_help(message):
        item = Recolector(message.lower())
        if item.data:
            print(message)
            data = json.dumps(item.data, indent = 2)
            print(data)
            print("+-"*40)
