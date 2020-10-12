from karim import LOCALHOST
from karim.classes.mq_bot import MQBot
import os, logging
import telegram
from telegram.ext.updater import Updater
from telegram.utils.request import Request
from karim.secrets import secrets
from karim.bot import telebot
from telegram.ext import messagequeue as mq


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    # SET UP REDIS SESSION CONNECTOR

    # Initialize Bot
    BOT_TOKEN = secrets.get_var('BOT_TOKEN')
    URL = secrets.get_var('SERVER_APP_DOMAIN')
    PORT = int(os.environ.get('PORT', 5000))
    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    # set connection pool size for bot 
    request = Request(con_pool_size=8)
    testbot = MQBot(BOT_TOKEN, request=request, mqueue=q)
    updater = telegram.ext.updater.Updater(bot=testbot, use_context=True)
    # SET UP BOT COMMAND HANDLERS
    telebot.setup(updater)
    if LOCALHOST:
        updater.start_polling()
    else:
        # Setup Telegram Webhook
        print('STARTING WEBHOOK')
        updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=BOT_TOKEN)
        print('WEBHOOK STARTED - SETTING UP WEBHOOK')
        updater.bot.set_webhook('{URL}/{HOOK}'.format(URL=URL, HOOK=BOT_TOKEN))
        print('WEBHOOK SET UP CORRECTLY')
        updater.idle()