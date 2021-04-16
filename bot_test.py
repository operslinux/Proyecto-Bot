from threading import Thread
from time import sleep
import json

from telegram import (
        Update,
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        ParseMode,
        )

from telegram.ext import (
        Updater,
        CommandHandler,
        MessageHandler,
        Filters,
        ConversationHandler,
        CallbackContext,
        CallbackQueryHandler
        )
import logging
from custom_message_handler import HelpHandler
from process_help import Recolector

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
        )
logger = logging.getLogger(__name__)

from safe_data import Data

data = Data()

TOKEN = data.token2
CHANNEL_URL = data.channel_url

def help_user(update, context):
    try:
        name = update.message.from_user.first_name
    except:
        name = update.message.chat.first_name
    item = Recolector(update.message.text.lower())
    if any((
            item.data["installables"],
            item.data["installation"],
            item.data["installable_keywords"],
            item.data["custom_from_keywords"],
            )): pass
    data = json.dumps(item.data, indent = 4, ensure_ascii = False)
    html_message = format_data_suggestion(item.data, name)

    msg_ask_id = update.message.message_id
    update.message.reply_html(text = html_message, reply_to_message_id = msg_ask_id, disable_web_page_preview = True)

def format_data_suggestion(data, name):
    print(json.dumps(data, indent = 4, ensure_ascii = False))
    content = ""
    custom_text = False
    if any((
            data["installable_keywords"],
            data["custom_from_keywords"],
            )):
        title = f"Hola, {name}, leí tu mensaje, busqué un poco y encontré algunas cosas:"
    else:
        title = f"Hola, {name}, veo que necesitas ayuda, ¿podrías ser más específico?"

    if data["installables"]:
        if data["installable_keywords"]:
            for i in data["installable_keywords"]:
                installable_post_id = data["installables"][i]["post_id"]
                if data["installable_keywords"][i]:
                    content +=  f'\n\nRelacionado con <a href="{CHANNEL_URL}/{installable_post_id}">{i}</a>:'
                    for post_title in data["installable_keywords"][i]:
                        post_id = data["installable_keywords"][i][post_title]["post_id"]
                        content_post_id = data["installable_keywords"][i][post_title]["post_id"]
                        content += f'\n<code>  ~ </code><a href="{CHANNEL_URL}/{content_post_id}">{post_title}</a>'
                else:
                    content += f"\n\nNada relacionado con <a href='{CHANNEL_URL}/{installable_post_id}'>{i}</a>."
    if data["custom_from_keywords"]:
        custom_text = "\n\nEsto podría interesarte:"
        for post_title in data["custom_from_keywords"]:
            post_id = data["custom_from_keywords"][post_title]["post_id"]
            custom_text += f"\n<code>  ~ </code><a href='{CHANNEL_URL}/{post_id}'>{post_title}</a>"

    if custom_text:
        content += custom_text

    return(title + content)


def main():
    global HelpHandler
    HelpHandler = HelpHandler()

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    custom_handler = MessageHandler(HelpHandler &(Filters.chat_type.group), help_user)

    dispatcher.add_handler(custom_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

