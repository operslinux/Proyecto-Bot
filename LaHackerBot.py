#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import logging
from telegram import *
from telegram.ext import *
from time import sleep
import qrcode
import os
from random import choice

INPUT_TEXT = 0
ruta = "data/admins.json"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    user = update.message.from_user

    test = update.message.reply_text(
        "Hola @" + "{} soy El Bot La Hacker coloca / (slash) para mas información".format(user["username"]))
    chat_id = test['chat_id']
    message_id = test['message_id']
    sleep(10)
    context.bot.deleteMessage(chat_id, message_id)


def redes(update, context):
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    keyboard = [[InlineKeyboardButton("YouTube", url="https://www.youtube.com/opersweenlinux")],
                [InlineKeyboardButton("Grupo de Facebook", url="https://www.facebook.com/groups/kaliparanovatos")],
                [InlineKeyboardButton("Pagina de Facebook", url="https://www.facebook.com/kalilinuxparanovatos/")],
                [InlineKeyboardButton("Grupo telegram", url="https://t.me/kalilinuxparanovatosoficcial")],
                [InlineKeyboardButton("Pagina Web", url="https://operslinux.com/")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Hola @" + "{} soy La Hacker, aqui te dejo la informacion: ".format(user["username"]),
        reply_markup=reply_markup

        )


def qr_command(update, context):
    update.message.reply_text('Enviame el texto para generarte tu QR')
    return INPUT_TEXT


def generate_qr(text):
    filename = "codeqr.jpg"
    img = qrcode.make(text)
    img.save(filename)
    return filename


def send_qr(filename, chat):
    chat.send_action(
        action=ChatAction.UPLOAD_PHOTO,
        timeout=None
    )
    chat.send_photo(
        photo=open(filename, 'rb')
    )
    os.unlink(filename)


def input_text(update, context):
    text = update.message.text
    filename = generate_qr(text)
    chat = update.message.chat
    send_qr(filename, chat)

    return ConversationHandler.END


"""Simplemente generamos una contraseña aleatoria"""


def password(update, context):
    length = 30
    values = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+ "
    passwd = ""
    passwd = passwd.join([choice(values) for _ in range(length)])
    test = update.message.reply_text(passwd)
    message_id = test['message_id']
    chat_id = test['chat_id']
    sleep(10)
    context.bot.deleteMessage(chat_id, message_id)


"""Se usara para dar avisos desde el grupo que sean admins,
           por ejemplo desde el grupo proyecto x """


def aviso(update, context):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    data = context.bot.get_chat_member(chat_id, user_id)
    mi_title = str(data['status'])

    if str(mi_title) == "administrador":

        messages = update.message.text
        find = "/aviso"
        replace = "Mensaje Automatico: "
        new_string = messages.replace(find, replace)
        chat_id_kali_linux = -1001328032477
        context.bot.send_message(chat_id_kali_linux, new_string)
    elif str(mi_title) == "creator":

        messages = update.message.text
        find = "/aviso"
        replace = "Mensaje Automatico: "
        new_string = messages.replace(find, replace)
        chat_id_kali_linux = -1001328032477
        context.bot.send_message(chat_id_kali_linux, new_string)

    else:
        update.message.reply_text("Usted no es administrador")


"""Simplemente de prueba para sacar los ids de los grupos o chats """


def ide(update, context):
    print(update.message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    print("Comenzando..")
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1642041332:AAGiTV4_LWC3jakhoLdXZFTdbFnvx-AQCuw", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("redes", redes))
    dp.add_handler(CommandHandler("pass", password))
    dp.add_handler(CommandHandler("aviso", aviso))
    dp.add_handler(CommandHandler("id", ide))
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler('qr', qr_command)
        ],
        states={
            INPUT_TEXT: [MessageHandler(Filters.text, input_text)]
        },
        fallbacks=[]
    ))

    # on noncommand i.e message - echo the message on Telegram

    # dp.add_handler(MessageHandler(Filters.text, echo))

    # dp.add_handler(MessageHandler(Filters.text, charla))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
