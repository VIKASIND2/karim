import os
from rq import Queue
from worker import conn
from instaclient import InstaClient
from telegram.ext.updater import Updater
from telegram.ext.defaults import Defaults
from telegram.utils.request import Request
from karim.classes.mq_bot import MQBot
from telegram import ParseMode
from telegram.ext import messagequeue as mq

LOCALHOST = True
queue = None
if os.environ.get('PORT') in (None, ""):
    # Code running locally
    LOCALHOST = True
    instaclient = InstaClient()
    if not os.path.exists('karim/bot/persistence'):
        os.makedirs('karim/bot/persistence')
else:
    LOCALHOST = False
    queue = Queue(connection=conn)
    instaclient = InstaClient(host=InstaClient.WEB_SERVER)

# Initialize Bot
from karim.secrets import secrets
from karim.bot import telebot
BOT_TOKEN = secrets.get_var('BOT_TOKEN')
URL = secrets.get_var('SERVER_APP_DOMAIN')
PORT = int(os.environ.get('PORT', 5000))
# set connection pool size for bot 
request = Request(con_pool_size=8)
testbot = MQBot(BOT_TOKEN, request=request, mqueue=q, defaults=Defaults(parse_mode=ParseMode.HTML))
updater = Updater(bot=testbot, use_context=True, defaults=Defaults(parse_mode=ParseMode.HTML))
q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
# SET UP BOT COMMAND HANDLERS
telebot.setup(updater)
        

