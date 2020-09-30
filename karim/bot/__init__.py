from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, Dispatcher
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup, ChatAction, Bot
from telegram.ext.dispatcher import run_async
from telegram.ext.updater import JobQueue
from queue import Queue  # in python 2 it should be "from Queue"
from threading import Thread
from datetime import datetime, timedelta
from functools import wraps
from telegram.utils.helpers import mention_html
import sys
import traceback
import json
import logging
import os
import html
import pickle

from karim.bot.texts  import *
from karim.classes import *
from karim.secrets import secrets
from karim import bot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("telegram.bot")
# GLOBAL VARIABLES - CONVERSATION
TIMEOUT = -2

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def create_menu(button_titles, callbacks, cols=1):
    print("BOT: menu()")
    keyboard = []
    index = 0
    row = []
    for title in button_titles:
        keyboard_button = InlineKeyboardButton(
            title, callback_data=callbacks[index])
        if len(row) < cols:
            row.append(keyboard_button)
        else:
            keyboard.append(row)
            row = []
            row.append(keyboard_button)
        index += 1
    if row != "":
        keyboard.append(row)
    markup = InlineKeyboardMarkup(keyboard)
    return markup


def error(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        'An exception was raised while handling an update\n'
        '<pre>update = {}</pre>\n\n'
        '<pre>context.chat_data = {}</pre>\n\n'
        '<pre>context.user_data = {}</pre>\n\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(tb)
    )

    # Finally, send the message
    devs = secrets.get_var('DEVS')
    for dev in devs:
        context.bot.send_message(chat_id=dev, text=message, parse_mode=ParseMode.HTML)


