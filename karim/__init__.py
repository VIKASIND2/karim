import os
import telegram
from flask import Flask
from telegram import base
from telegram.ext.updater import Updater
from telegram.utils.request import Request
import telethon
from karim.secrets import secrets


# SET UP REDIS SESSION CONNECTOR
LOCALHOST = True
connector = None
if os.environ.get('PORT') in (None, ""):
    # Code running locally
    LOCALHOST = True
    if not os.path.exists('karim/bot/persistence'):
        os.makedirs('karim/bot/persistence')
else:
    LOCALHOST = False

# Initialize Bot
from karim.bot import telebot
BOT_TOKEN = secrets.get_var('BOT_TOKEN')
URL = secrets.get_var('SERVER_APP_DOMAIN')
PORT = int(os.environ.get('PORT', '8443'))
request = Request(con_pool_size=8)
updater = Updater(BOT_TOKEN, use_context=True)
telebot.setup(updater)
# Setup Telegram Webhook
print('STARTING WEBHOOK')
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=BOT_TOKEN)
print('WEBHOOK STARTED - SETTING UP WEBHOOK')
updater.bot.set_webhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))
print('WEBHOOK SET UP CORRECTLY')
updater.idle()

# Initialize Flask App
app = Flask(__name__)

# Import Flask Routes
from karim import routes
