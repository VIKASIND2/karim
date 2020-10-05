import os
import re
import telegram
from flask import Flask
from telegram.utils.request import Request
from karim.secrets import secrets
from karim.bot import telebot
from telegram.error import RetryAfter
import time
from karim.classes.teleredis import RedisSession
import redis

# Initialize Bot
BOT_TOKEN = secrets.get_var('BOT_TOKEN')
URL = secrets.get_var('SERVER_APP_DOMAIN')
request = Request(con_pool_size=8)
bot = telegram.Bot(token=BOT_TOKEN, request=request)
update_queue = telebot.setup(bot)

# Setup Telegram Webhook
try:
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))
except RetryAfter:
    time.sleep(4)
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))

# SET UP REDIS SESSION CONNECTOR
LOCALHOST = True
redis_connector = None
if os.environ.get('PORT') in (None, ""):
    # Code running locally
    LOCALHOST = True
    if not os.path.exists('karim/bot/persistence'):
        os.makedirs('karim/bot/persistence')
else:
    LOCALHOST = False
    redis_connector = redis.Redis(host=secrets.get_var('REDIS_URL'), port=14909, db=0, decode_responses=False)


# Initialize Flask App
app = Flask(__name__)

# Import Flask Routes
from karim import routes
