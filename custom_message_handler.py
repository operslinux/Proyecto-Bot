import re
from help_filter import needs_help, confirm_help
from get_tags import process_message_tags
from utils import clean_text

def process_message(message):
    message = clean_text(message)
    if needs_help(message):
        if confirm_help(message):
            process_message_tags(message)


############################################# PRUEBAS ################################
import json
# Cargar chat exportado.
with open("result.json", "r") as file:
    chat_history = json.load(file)
    file.close()
chat = chat_history["messages"]
messages = [item["text"] for item in chat if isinstance((item["text"]), str)]

for message in messages:
    process_message(message)
