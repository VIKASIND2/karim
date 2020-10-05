import telegram
from flask import Flask
from telegram.utils.request import Request
from karim.secrets import secrets
from karim.bot import telebot
from telegram.error import RetryAfter
import time

# Initialize Bot
BOT_TOKEN = secrets.get_var('BOT_TOKEN')
URL = secrets.get_var('SERVER_APP_DOMAIN')
request = Request(con_pool_size=8)
bot = telegram.Bot(token=BOT_TOKEN, request=request)
update_queue = telebot.setup(bot)

# Setup Telegram Webhook
print('LOGS: Bot Token: ', BOT_TOKEN)
print('LOGS: URL: ', URL)
try:
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))
except RetryAfter:
    time.sleep(4)
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))


# Initialize Flask App
app = Flask(__name__)

# Import Flask Routes
from karim import routes
