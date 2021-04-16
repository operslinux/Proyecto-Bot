import json# {{{
from threading import Thread
from time import sleep

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

from rename import Installable, InstallableItem, CustomItem
from utils import (
        sort_by_letter, make_alphabet_keyboard,
        make_programs_message, register_installable_to_database,
        register_to_installables, register_custom_to_database,
        get_id, get_file_chunks, get_msg_id, is_installable,
        has_installable
        )

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
        )

logger = logging.getLogger(__name__)# }}}

from safe_data import Data
data = Data()

TOKEN = data.token1
CHANNEL_ID = data.channel_id
CHANNEL_URL = data.channel_url
POSTING = False

CHOICE, LETTER, REGISTER, TITLE, DESCRIPTION, KEYWORDS, URLS, FILES, FINISH = range(9)
NAME, I_DESCRIPTION, HOMEPAGE, DOWNLOAD, DOCS, I_FINISH = range(6)
C_TITLE, C_DESCRIPTION, C_KEYWORDS, C_URLS, C_FILES, C_FINISH = range(6)

REGISTERS = {}
I_REGISTERS = {}
C_REGISTERS = {}

def reload_installables():
    global ordered
    installables = json.loads(open("resources/installables.json", "r").read())
    ordered = sort_by_letter(installables)

"+-+-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-"

def start_register(update, context):
    titles = ["Instalable", "Sección de instalable", "Personalizado"]
    keyboard = [
            [InlineKeyboardButton(item, callback_data = item)] for item in titles]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Selecciona el tipo de contenido a registrar.\nDetén el registro con /cancelar en cualquier momento."
    update.message.reply_text(text, reply_markup = reply_markup)

def installable_start(update, context):
    chat_id = get_id(update)
    message_id = get_msg_id(update)
    text = "Muy bien, ¿cuál es el nombre del instalable que deseas registrar?"
    context.bot.edit_message_text(chat_id = chat_id, message_id = message_id, text = text)

    return NAME

def register_installable_name(update, context):
    name = update.message.text
    I_REGISTERS[get_id(update)] = Installable(name)
    if is_installable(name):
        update.message.reply_markdown(f"*ADVERTENCIA*: {name} ya ha sido registrado anteriormente.\n" + \
                "Presiona /cancelar para abortar. \n Presiona /continuar si estás seguro de reemplazarlo.")
        return NAME
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    update.message.reply_text("Bien, ahora envíame la descripción.",reply_markup = reply_markup)

    return I_DESCRIPTION


def register_installable_name_nw(update, context):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    update.message.reply_text("Bien, ahora envíame la descripción.", reply_markup = reply_markup)

    return I_DESCRIPTION


def register_installable_description(update, context):
    chat_id = get_id(update)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    if update.callback_query is None:
        text = update.message.text
        I_REGISTERS[chat_id].set_description(text)
        update.message.reply_text("Descripción registrada!\n" + \
                "Ahora envíame el enlace de la página principal.", reply_markup = reply_markup)
    else:
        context.bot.edit_message_text(chat_id = update.callback_query.message.chat.id,
                message_id = get_msg_id(update),
                text = "Descripción omitida!\n" + "Ahora envíame el enlace de la página principal",
                reply_markup = reply_markup)
    return HOMEPAGE

def register_homepage(update, context):
    chat_id = get_id(update)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    if update.callback_query is None:
        entities = update.message.entities
        text = update.message.text
        urled = [entity for entity in entities if entity["type"] == "url"]
        urls = [text[entity["offset"]:entity["offset"]+entity["length"]] for entity in urled]
        if len(urls) > 1:
            update.message.reply_text("No se puede registrar más de un enlace a la vez, inténtalo de nuevo.")
            return HOMEPAGE
        else:
            homepage = urls[0]
            I_REGISTERS[chat_id].set_homepage(homepage)
            update.message.reply_text(
                    "Página principal registrada!\nAhora envíame el enlace de la página de descarga.",
                    reply_markup = reply_markup)
    else:
        context.bot.edit_message_text(chat_id = update.callback_query.message.chat.id,
                message_id = get_msg_id(update),
                text = "Página principal omitida!\nAhora envíame el enlace de la página de descarga.",
                reply_markup = reply_markup
                )

    return DOWNLOAD

def register_download(update, context):
    chat_id = get_id(update)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    if update.callback_query is None:
        entities = update.message.entities
        text = update.message.text
        urled = [entity for entity in entities if entity["type"] == "url"]
        urls = [text[entity["offset"]:entity["offset"]+entity["length"]] for entity in urled]
        if len(urls) > 1:
            update.message.reply_text("No se puede registrar más de un enlace a la vez, inténtalo de nuevo.")
            return DOWNLOAD
        else:
            download = urls[0]
            I_REGISTERS[chat_id].set_download_page(download)
            update.message.reply_text(
                    "Enlace registrado!\nAhora envíame el enlace de la documentación.",
                    reply_markup = reply_markup)
    else:
        context.bot.edit_message_text(chat_id = update.callback_query.message.chat.id,
                message_id = get_msg_id(update),
                text = "Página principal omitida!\nAhora envíame el enlace de la documentación.",
                reply_markup = reply_markup
                )
    return DOCS

def register_docs(update, context):
    chat_id = get_id(update)
    if update.callback_query is None:
        entities = update.message.entities
        text = update.message.text
        urled = [entity for entity in entities if entity["type"] == "url"]
        urls = [text[entity["offset"]:entity["offset"]+entity["length"]] for entity in urled]
        if len(urls) > 1:
            update.message.reply_text("No se puede registrar más de un enlace a la vez, inténtalo de nuevo.")
            return DOCS
        else:
            docs = urls[0]
            I_REGISTERS[chat_id].set_docs(docs)
            update.message.reply_text(
                    "Documentación registrada! eso fue todo!")
            html_text = I_REGISTERS[chat_id].format_data()
            text = "Esto es lo que se ha registrado, escribe <b><i>Correcto</i></b> si lo es, o " + \
                    "<b><i>Incorrecto</i></b> si no lo es."
            update.message.reply_html(text = html_text, disable_web_page_preview = True)
            update.message.reply_html(text = text)
    else:
        message_id = get_msg_id(update)
        context.bot.delete_message(message_id = message_id, chat_id = get_id(update))
        html_text = I_REGISTERS[chat_id].format_data()
        update.callback_query.message.reply_text("Documentación omitida.")
        text = "Esto es lo que se ha registrado, escribe <b><i>Correcto</i></b> si lo es, o " + \
                "<b><i>Incorrecto</i></b> si no lo es."
        update.callback_query.message.reply_html(text = html_text, disable_web_page_preview = True)
        update.callback_query.message.reply_html(text = text)

    return I_FINISH

def finish_installable_registering(update, context):
    answer = update.message.text
    if answer.lower() == "correcto":
        update.message.reply_text("Gracias, los aportes serán publicados.")
        post_thread = Thread(target = register_installable, args = [update, context])
        post_thread.start()
    elif answer.lower() == "incorrecto":
        update.message.reply_text("Los datos no se han registrado, operación cancelada.")
    return ConversationHandler.END

def register_installable(update, context):
    # Para evitar que colisionen dos usuarios registrando datos
    global POSTING
    if POSTING:
        while POSTING:
            sleep(2)
    POSTING = True
    chat_id = get_id(update)
    post_id = post_installable(update, context)
    I_REGISTERS[chat_id].post_id = post_id
    register_installable_to_database(I_REGISTERS[chat_id].name, I_REGISTERS[chat_id].get_data_dict())
    POSTING = False

def post_installable(update, context):
    chat_id = get_id(update)
    description = I_REGISTERS[chat_id].get_description()
    post = context.bot.send_message(chat_id = CHANNEL_ID, text = description, parse_mode = ParseMode.HTML)
    post_id = post.message_id

    return post_id

def send_keyboard(update, context):
    reload_installables()
    selection = update.callback_query.data# {{{
    chat_id = get_id(update)
    message_id = get_msg_id(update)

    # Tomar acciones dependiendo de la selección del usuario.
    if selection == "Sección de instalable":
        # Teclado con letras como text y callback_data.
        keyboard = make_alphabet_keyboard(8, ordered)
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Elije la inicial del instalable:"
        context.bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = reply_markup)

        return LETTER

    elif selection == "Instalable":
        pass

    elif selection == "Personalizado":
        pass
# }}}

def send_numbers(update, context):
    chat_id = get_id(update)# {{{
    message_id = get_msg_id(update)

    # Letra elegida por el usuario
    chosen_letter = update.callback_query.data
    programs = ordered[chosen_letter]

    # Si se encuentran programas con esa inicial, listarlos
    # si no, notificar, enviar teclado de nuevo y esperar por una respuesta.
    if programs:
        text, keyboard = make_programs_message(programs)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = reply_markup)

        return REGISTER
    else:
        keyboard = make_alphabet_keyboard(8, ordered)
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Edita el mensage de manera que no sea igual al anterior
        try:
            context.bot.edit_message_text(
                    "No se ha encontrado ningún programa con esta inicial,\nSelecciona otra:",
                    chat_id = chat_id,
                    message_id = message_id,
                    reply_markup = reply_markup
                    )
        except:
            context.bot.edit_message_text(
                    "No se ha encontrado ningún programa con esta inicial, \nSelecciona otra:",
                    chat_id = chat_id,
                    message_id = message_id,
                    reply_markup = reply_markup
                    )

# }}}

def continue_registering(update, context):
    program = update.callback_query.data# {{{
    chat_id = get_id(update)
    message_id = get_msg_id(update)

    if program == "Seleccionar otra inicial":
        keyboard = make_alphabet_keyboard(8, ordered)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(
                "Selecciona la inicial del instalable:",
                chat_id = chat_id,
                message_id = message_id,
                reply_markup = reply_markup
                )
        return LETTER
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")]])
    update.callback_query.answer(f"Se ha seleccionado {program}!")
    context.bot.edit_message_text(
            f"Dime el título por favor:",
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = reply_markup
            )
    REGISTERS[chat_id] = InstallableItem(program, CHANNEL_URL)
    return TITLE
# }}}

def register_title(update, context):
    chat_id = get_id(update)
    title = update.message.text
    REGISTERS[chat_id].set_title(title)
    text = """Muy bien, ¿cuál será la descripción? Envíamela por favor."""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")]])
    update.message.reply_text(text = text, reply_markup = reply_markup)
    return DESCRIPTION

def register_description(update, context):
    chat_id = get_id(update)
    description = update.message.text
    REGISTERS[chat_id].set_description(description)
    text = """Perfecto, ahora dime las palabras clave, necesito que las escribas separadas por comas, ej:\nkali, linux, grub, modificar
    """
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")]])
    update.message.reply_text(text = text, reply_markup = reply_markup)
    return KEYWORDS

def register_keywords(update, context):
    chat_id = get_id(update)
    REGISTERS[chat_id].set_keywords(update.message.text)
    text = "Vale, ahora puedes enviarme los enlaces relacionados.\nPresiona el botón cuando termines o para omitir el registro."
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "Hecho")]])
    update.message.reply_text(text = text, reply_markup = reply_markup)
    return URLS

def register_urls(update, context):
    chat_id = get_id(update)
    if update.callback_query is None:
        x = update.message.entities
        entities = list([m for m in x if m["type"] == "url"])
        if not entities:
            update.message.reply_text("No se encontraron urls en el mensaje.")
            return URLS
        text = update.message.text
        REGISTERS[chat_id].set_urls(text, update.message.entities)

        update.message.reply_text("Registrado.")
    else:
        message_id = get_msg_id(update)

        context.bot.delete_message(chat_id = chat_id, message_id = message_id)
        text = "Muy bien, ahora envíame los documentos y presiona el botón cuando termines, o para omitir el registro."
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "Hecho")]])
        update.callback_query.message.reply_text(text = text, reply_markup = reply_markup)

        return FILES

def register_files(update, context):
    chat_id = get_id(update)
    if update.callback_query is None:
        if update.message.document is None:
            update.message.reply_text("Tienes que enviar los archivos como documentos.")
        else:
            file_id = update.message.document.file_id
            REGISTERS[chat_id].add_file(file_id)
    else:
        message_id = get_msg_id(update)

        update.callback_query.answer("Datos registrados exitosamente!")
        context.bot.delete_message(message_id = message_id, chat_id = chat_id)
        html_text = REGISTERS[chat_id].format_data()
        text = "Excelente, esto es lo que se ha registrado, escribe <b><i>Correcto</i></b> si lo es, o " + \
                "<b><i>Incorrecto</i></b> si no lo es."
        update.callback_query.message.reply_html(text = html_text, disable_web_page_preview = True)
        update.callback_query.message.reply_html(text = text)

        return FINISH

def finish_registering(update, context):
    answer = update.message.text
    if answer.lower() == "correcto":
        update.message.reply_text("Gracias, los aportes serán publicados.")
        post_thread = Thread(target = post, args = [update, context])
        post_thread.start()
    elif answer.lower() == "incorrecto":
        update.message.reply_text("Los datos no se han registrado, operación cancelada.")
    return ConversationHandler.END

def post(update, context):
    # Para evitar que colisionen dos usuarios registrando datos
    global POSTING
    if POSTING:
        while POSTING:
            sleep(2)
    POSTING = True
    chat_id = get_id(update)
    post_id = post_content(update, context)
    REGISTERS[chat_id].post_id = post_id
    register_to_installables(REGISTERS[chat_id].get_data_dict())
    POSTING = False

def post_content(update, context):
    chat_id = get_id(update)
    description = REGISTERS[chat_id].get_description()
    post = context.bot.send_message(chat_id = CHANNEL_ID, text = description, parse_mode = ParseMode.HTML)
    post_id = post.message_id
    files = REGISTERS[chat_id].files
    if files:
        if len(files) > 1:
            # The second argument is the lenght for the chunks
            chunks = get_file_chunks(files, 10)
            for chunk in chunks:
                context.bot.send_media_group(chat_id = CHANNEL_ID, media = chunk, reply_to_message_id = post_id, disable_notification = True)
                sleep(35)
        else:
            context.bot.send_document(chat_id = CHANNEL_ID, document = files[0], reply_to_message_id = post_id, disable_notification = True)

    return post_id

def send_keyboard(update, context):
    reload_installables()
    selection = update.callback_query.data# {{{
    chat_id = get_id(update)
    message_id = get_msg_id(update)

    # Tomar acciones dependiendo de la selección del usuario.
    if selection == "Sección de instalable":
        # Teclado con letras como text y callback_data.
        keyboard = make_alphabet_keyboard(8, ordered)
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Elije la inicial del instalable:"
        context.bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = reply_markup)

        return LETTER

    elif selection == "Instalable":
        pass

    elif selection == "Personalizado":
        pass
# }}}

def send_numbers(update, context):
    chat_id = get_id(update)# {{{
    message_id = get_msg_id(update)

    # Letra elegida por el usuario
    chosen_letter = update.callback_query.data
    programs = ordered[chosen_letter]

    # Si se encuentran programas con esa inicial, listarlos
    # si no, notificar, enviar teclado de nuevo y esperar por una respuesta.
    if programs:
        text, keyboard = make_programs_message(programs)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text, chat_id = chat_id, message_id = message_id, reply_markup = reply_markup)

        return REGISTER
    else:
        keyboard = make_alphabet_keyboard(8, ordered)
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Edita el mensage de manera que no sea igual al anterior
        try:
            context.bot.edit_message_text(
                    "No se ha encontrado ningún programa con esta inicial,\nSelecciona otra:",
                    chat_id = chat_id,
                    message_id = message_id,
                    reply_markup = reply_markup
                    )
        except:
            context.bot.edit_message_text(
                    "No se ha encontrado ningún programa con esta inicial, \nSelecciona otra:",
                    chat_id = chat_id,
                    message_id = message_id,
                    reply_markup = reply_markup
                    )

# }}}

def continue_registering(update, context):
    program = update.callback_query.data# {{{
    chat_id = get_id(update)
    message_id = get_msg_id(update)

    if program == "Seleccionar otra inicial":
        keyboard = make_alphabet_keyboard(8, ordered)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(
                "Selecciona la inicial del instalable:",
                chat_id = chat_id,
                message_id = message_id,
                reply_markup = reply_markup
                )
        return LETTER
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")]])
    update.callback_query.answer(f"Se ha seleccionado {program}!")
    context.bot.edit_message_text(
            f"Dime el título por favor:",
            chat_id = chat_id,
            message_id = message_id,
            reply_markup = reply_markup
            )
    REGISTERS[chat_id] = InstallableItem(program, CHANNEL_URL)
    return TITLE
# }}}

def register_title(update, context):
    chat_id = get_id(update)
    title = update.message.text
    REGISTERS[chat_id].set_title(title)
    text = """Muy bien, ¿cuál será la descripción? Envíamela por favor."""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")]])
    update.message.reply_text(text = text, reply_markup = reply_markup)
    return DESCRIPTION

def register_description(update, context):
    chat_id = get_id(update)
    description = update.message.text
    REGISTERS[chat_id].set_description(description)
    text = """Perfecto, ahora dime las palabras clave, necesito que las escribas separadas por comas, ej:\nkali, linux, grub, modificar
    """
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Cancelar operación", callback_data = "Cancelar operación")]])
    update.message.reply_text(text = text, reply_markup = reply_markup)
    return KEYWORDS

def register_keywords(update, context):
    chat_id = get_id(update)
    REGISTERS[chat_id].set_keywords(update.message.text)
    text = "Vale, ahora puedes enviarme los enlaces relacionados.\nPresiona el botón cuando termines o para omitir el registro."
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "Hecho")]])
    update.message.reply_text(text = text, reply_markup = reply_markup)
    return URLS

def register_urls(update, context):
    chat_id = get_id(update)
    if update.callback_query is None:
        x = update.message.entities
        entities = list([m for m in x if m["type"] == "url"])
        if not entities:
            update.message.reply_text("No se encontraron urls en el mensaje.")
            return URLS
        text = update.message.text
        REGISTERS[chat_id].set_urls(text, update.message.entities)

        update.message.reply_text("Registrado.")
    else:
        message_id = get_msg_id(update)

        context.bot.delete_message(chat_id = chat_id, message_id = message_id)
        text = "Muy bien, ahora envíame los documentos y presiona el botón cuando termines, o para omitir el registro."
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "Hecho")]])
        update.callback_query.message.reply_text(text = text, reply_markup = reply_markup)

        return FILES

def register_files(update, context):
    chat_id = get_id(update)
    if update.callback_query is None:
        if update.message.document is None:
            update.message.reply_text("Tienes que enviar los archivos como documentos.")
        else:
            file_id = update.message.document.file_id
            REGISTERS[chat_id].add_file(file_id)
    else:
        message_id = get_msg_id(update)

        update.callback_query.answer("Datos registrados exitosamente!")
        context.bot.delete_message(message_id = message_id, chat_id = chat_id)
        html_text = REGISTERS[chat_id].format_data()
        text = "Excelente, esto es lo que se ha registrado, escribe <b><i>Correcto</i></b> si lo es, o " + \
                "<b><i>Incorrecto</i></b> si no lo es."
        update.callback_query.message.reply_html(text = html_text, disable_web_page_preview = True)
        update.callback_query.message.reply_html(text = text)

        return FINISH

def finish_registering(update, context):
    answer = update.message.text
    if answer.lower() == "correcto":
        update.message.reply_text("Gracias, los aportes serán publicados.")
        post_thread = Thread(target = post, args = [update, context])
        post_thread.start()
    elif answer.lower() == "incorrecto":
        update.message.reply_text("Los datos no se han registrado, operación cancelada.")
    return ConversationHandler.END

def custom_start(update, context):
    context.bot.edit_message_text(
            text = "Muy bien, comienza diciéndome el título.",
            message_id = get_msg_id(update),
            chat_id = get_id(update))
    return C_TITLE

def set_title_custom(update, context):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    title = update.message.text
    chat_id = get_id(update)
    C_REGISTERS[chat_id] = CustomItem(title)
    update.message.reply_text("Título registrado, ahora escríbeme la descripción.",
            reply_markup = reply_markup)

    return C_DESCRIPTION

def set_description_custom(update, context):
    chat_id = get_id(update)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Omitir", callback_data = "omitir")]])
    if update.callback_query is None:
        update.message.reply_text("Muy bien, ahora envíame las palabras clave " + \
                "deben estar separadas por comas.")
        C_REGISTERS[chat_id].set_description(update.message.text)
    else:
        message_id = get_msg_id(update)
        chat_id = get_id(update)
        text = "Descripción omitida, ahora envíame las palabras clave, deben estar separadas por comas."
        context.bot.edit_message_text(text = text, chat_id = chat_id, message_id = message_id)
    return C_KEYWORDS

def set_keywords_custom(update, context):
    chat_id = get_id(update)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "hecho")]])
    C_REGISTERS[chat_id].set_keywords(update.message.text)

    title = C_REGISTERS[chat_id].title
    desc = C_REGISTERS[chat_id].description
    keywords = C_REGISTERS[chat_id].keywords
    # Si se encuentra indicio de que el usuario está registrando información de un instalable
    # que existe, advertirlo y pedirle que registre el contenido en la seccion de instalables.
    installables =  has_installable(title, desc, keywords)
    if installables:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("→ Cancelar Operación ←", callback_data = "Cancelar Operación")],
            [InlineKeyboardButton("Hecho", callback_data = "hecho")]
            ])
        html_text = "<b>¡ADVERTENCIA!</b>\nSe ha detectado que estás registrando contenido relacionado con un artículo:\n("
        for idx, i in enumerate(installables, 1):
            if idx != len(installables):
                html_text += f"<a href='{CHANNEL_URL}/{installables[i]}'>{i}</a>, "
            else:
                html_text += f"<a href='{CHANNEL_URL}/{installables[i]}'>{i}</a>."
        html_text += ")\nPor favor regístralo en 'Sección de instalable' introduce el comando /cancelar o presiona el botón ↓ ↓.\n"
        html_text += "Si estás seguro de continuar, el contenido será mal indexado, pero continúa enviándome los enlaces relacionados."
        update.message.reply_html(html_text, reply_markup = reply_markup, disable_web_page_preview = True)
    else:
        text = "Listo, ahora envíame los enlaces a registrar."
        update.message.reply_text(text, reply_markup = reply_markup)

    return C_URLS

def set_urls_custom(update, context):
    chat_id = get_id(update)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "hecho")]])
    if update.callback_query is None:
        x = update.message.entities
        entities = list([m for m in x if m["type"] == "url"])
        if not entities:
            update.message.reply_text("No se encontraron urls en el mensaje.")
            return C_URLS
        text = update.message.text
        C_REGISTERS[chat_id].set_urls(text, entities)
        update.message.reply_text("Correcto.")
    elif update.callback_query is not None:
        message_id = get_msg_id(update)

        context.bot.delete_message(chat_id = chat_id, message_id = message_id)
        text = "Muy bien, ahora envíame los documentos."
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Hecho", callback_data = "hecho")]])
        update.callback_query.message.reply_text(text = text, reply_markup = reply_markup)

        return C_FILES

def set_files_custom(update, context):
    chat_id = get_id(update)
    if update.callback_query is None:
        if update.message.document is None:
            update.message.reply_text("Debes enviarme los archivos como documentos.")
        else:
            file_id = update.message.document.file_id
            C_REGISTERS[chat_id].add_file(file_id)
    else:
        message_id = get_msg_id(update)

        update.callback_query.answer("¡Gracias! verifíca la info por favor")
        context.bot.delete_message(message_id = message_id, chat_id = chat_id)
        html_text = C_REGISTERS[chat_id].format_data()
        text = "Esto es lo que se ha registrado, escribe <b><i>Correcto</i></b> si lo es, o " + \
                "<b><i>Incorrecto</i></b> si no lo es."
        update.callback_query.message.reply_html(text = html_text, disable_web_page_preview = True)
        update.callback_query.message.reply_html(text = text)

        return C_FINISH

def finish_registering_custom(update, context):
    answer = update.message.text
    if answer.lower() == "correcto":
        update.message.reply_text("Gracias, los aportes serán publicados.")
        post_thread = Thread(target = register_custom, args = [update, context])
        post_thread.start()
    elif answer.lower() == "incorrecto":
        update.message.reply_text("Los datos no se han registrado, operación cancelada.")
    return ConversationHandler.END

def register_custom(update, context):
    # Para evitar que colisionen dos usuarios registrando datos
    global POSTING
    if POSTING:
        while POSTING:
            sleep(2)
    POSTING = True
    chat_id = get_id(update)
    post_id = post_custom(update, context)
    C_REGISTERS[chat_id].post_id = post_id
    register_custom_to_database(C_REGISTERS[chat_id].title, C_REGISTERS[chat_id].get_data_dict())
    POSTING = False

def post_custom(update, context):
    chat_id = get_id(update)
    description = C_REGISTERS[chat_id].get_description()
    post = context.bot.send_message(chat_id = CHANNEL_ID, text = description, parse_mode = ParseMode.HTML)
    post_id = post.message_id
    files = C_REGISTERS[chat_id].files
    if files:
        if len(files) > 1:
            # The second argument is the lenght for the chunks
            chunks = get_file_chunks(files, 10)
            for chunk in chunks:
                context.bot.send_media_group(chat_id = CHANNEL_ID, media = chunk, reply_to_message_id = post_id, disable_notification = True)
                sleep(35)
        else:
            context.bot.send_document(chat_id = CHANNEL_ID, document = files[0], reply_to_message_id = post_id, disable_notification = True)

    return post_id

def finish_registering_custom_failed(update, context):
    if update.message is not None:
        update.message.reply_text("No te entendí, ¿puedes repetirmelo?")

"+-+-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-"

def cancel(update, context):
    text = "Operación cancelada."
    if update.message is not None:
        update.message.reply_text(text)
    elif update.callback_query is not None:
        message_id = get_msg_id(update)
        chat_id = get_id(update)
        context.bot.edit_message_text(text = text, chat_id = chat_id, message_id = message_id)
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    start_register_handler = CommandHandler("registrar", start_register)

    installable_register = ConversationHandler(# {{{
            entry_points = [
                CallbackQueryHandler(pattern = "^(Instalable)$", callback = installable_start)
                ],
            states = {
                NAME: [
                    CommandHandler("continuar", register_installable_name_nw),
                    MessageHandler(Filters.text &(~ Filters.command) &(~ Filters.update.edited_message), register_installable_name),
                    ],
                I_DESCRIPTION: [
                    MessageHandler(Filters.text &(~ Filters.command) &(~ Filters.update.edited_message), register_installable_description),
                    CallbackQueryHandler(pattern = "omitir", callback = register_installable_description)
                    ],
                HOMEPAGE: [
                    MessageHandler(Filters.entity("url") &(~ Filters.update.edited_message), register_homepage),
                    CallbackQueryHandler(pattern = "omitir", callback = register_homepage)
                    ],
                DOWNLOAD: [
                    MessageHandler(Filters.entity("url") &(~ Filters.update.edited_message), register_download),
                    CallbackQueryHandler(pattern = "omitir", callback = register_download)
                    ],
                DOCS: [
                    MessageHandler(Filters.entity("url") &(~ Filters.update.edited_message), register_docs),
                    CallbackQueryHandler(pattern = "omitir", callback = register_docs)
                    ],
                I_FINISH: [
                    MessageHandler(Filters.regex("^(Correcto|correcto|Incorrecto|incorrecto)$") &(~ Filters.update.edited_message), finish_installable_registering),
                    MessageHandler(Filters.text & (~ Filters.command), finish_registering_custom_failed)
                    ],
                },
            fallbacks = [
                CommandHandler("cancelar", cancel),
                CallbackQueryHandler(pattern = "Cancelar", callback = cancel)
                ]
            )# }}}

    installable_item_register = ConversationHandler(# {{{
            entry_points = [
                CallbackQueryHandler(pattern = "^(Sección de instalable)$", callback = send_keyboard)
                ],
            states = {
                LETTER: [
                    CallbackQueryHandler(pattern = "^(a|b|c|d|e|f|g|h|i|j|k|l|m|n|ñ|o|p|q|r|s|t|u|v|w|x|y|z)$", callback = send_numbers)
                    ],
                REGISTER: [
                    CallbackQueryHandler(pattern = "Cancelar operación", callback = cancel),
                    CallbackQueryHandler(pattern = "", callback = continue_registering)
                    ],
                TITLE:[
                    MessageHandler(Filters.text & (~ Filters.update.edited_message) & (~ Filters.command), register_title)
                    ],
                DESCRIPTION: [
                    MessageHandler(Filters.text & (~ Filters.update.edited_message) & (~ Filters.command), register_description)
                    ],
                KEYWORDS: [
                    MessageHandler(Filters.text & (~ Filters.update.edited_message) & (~ Filters.command), register_keywords)
                    ],
                URLS: [
                    MessageHandler(Filters.entity("url") &(~ Filters.update.edited_message), register_urls),
                    CallbackQueryHandler(pattern = "Hecho", callback = register_urls),
                    ],
                FILES: [
                    CallbackQueryHandler(pattern = "Hecho", callback = register_files),
                    MessageHandler(
                        Filters.document|Filters.photo|Filters.audio|Filters.video,
                        register_files
                        )
                    ],
                FINISH: [
                    MessageHandler(Filters.regex("^(Correcto|Incorrecto|correcto|incorrecto)$")&(~ Filters.update.edited_message), finish_registering),
                    MessageHandler(Filters.text & (~ Filters.command), finish_registering_custom_failed)
                    ]
                },
            fallbacks = [
                CommandHandler("cancelar", cancel),
                CallbackQueryHandler(pattern = "Cancelar", callback = cancel)
                ],
            per_chat = True,
            per_user = True,
            #conversation_timeout = 20*60
            )# }}}

    custom_register = ConversationHandler(# {{{
            entry_points = [
                CallbackQueryHandler(pattern = "^(Personalizado)$", callback = custom_start)
                ],
            states = {
                C_TITLE: [
                    CommandHandler("cancelar", cancel),
                    MessageHandler(Filters.text & (~ Filters.update.edited_message), set_title_custom)
                    ],
                C_DESCRIPTION: [
                    CallbackQueryHandler(pattern = "omitir", callback = set_description_custom),
                    MessageHandler(Filters.text & (~ Filters.update.edited_message) & (~ Filters.command), set_description_custom)
                    ],
                C_KEYWORDS: [
                    MessageHandler(Filters.text & (~ Filters.update.edited_message) & (~ Filters.command), set_keywords_custom)
                    ],
                C_URLS: [
                    MessageHandler(Filters.text & (~ Filters.update.edited_message) & (~ Filters.command), set_urls_custom),
                    CallbackQueryHandler(pattern = "hecho", callback = set_urls_custom)
                    ],
                C_FILES: [
                    CallbackQueryHandler(pattern = "hecho", callback = set_files_custom),
                    MessageHandler(
                        Filters.document|Filters.photo|Filters.audio|Filters.video,
                        set_files_custom
                        )
                    ],
                C_FINISH: [
                    MessageHandler(Filters.regex("^(Correcto|correcto|incorrecto|Incorrecto)$") , finish_registering_custom),
                    MessageHandler(Filters.text & (~ Filters.command), finish_registering_custom_failed)
                    ]
                },
            fallbacks = [
                CommandHandler("cancelar", cancel),
                CallbackQueryHandler(pattern = "Cancelar Operación", callback = cancel)
                ]
            )# }}}

    dispatcher.add_handler(start_register_handler)

    dispatcher.add_handler(installable_register)
    dispatcher.add_handler(installable_item_register)
    dispatcher.add_handler(custom_register)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
