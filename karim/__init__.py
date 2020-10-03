import telegram
from flask import Flask
from telegram.utils.request import Request
from karim.secrets import secrets
from karim.bot import telebot

# Initialize Bot
BOT_TOKEN = secrets.get_var('BOT_TOKEN')
URL = secrets.get_var('SERVER_APP_DOMAIN')
request = Request(con_pool_size=8)
bot = telegram.Bot(token=BOT_TOKEN, request=request)
update_queue = telebot.setup(bot)

# Setup Telegram Webhook
s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))

# Initialize Flask App
app = Flask(__name__)

# Import Flask Routes
from karim import routes
