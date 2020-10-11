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
from karim.secrets import secrets

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("telegram.bot")
# GLOBAL VARIABLES - CONVERSATION
TIMEOUT = -2

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
        '<b>An exception was raised while handling an update</b>\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(tb)
    )

    # Finally, send the message
    devs = secrets.get_var('DEVS')
    for dev in devs:
        context.bot.send_message(chat_id=dev, text=message, parse_mode=ParseMode.HTML)


