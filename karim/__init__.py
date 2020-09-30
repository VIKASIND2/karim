import telegram
from flask import Flask
from karim.secrets import secrets
from karim.bot import telebot

# Initialize Bot
BOT_TOKEN = secrets.get_var('BOT_TOKEN')
URL = secrets.get_var('SERVER_APP_DOMAIN')
bot = telegram.Bot(token=BOT_TOKEN)
update_queue = telebot.setup(secrets.get_var('BOT_TOKEN'))

# Setup Telegram Webhook
s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))

# Initialize Flask App
app = Flask(__name__)

# Import Flask Routes
from karim import routes
