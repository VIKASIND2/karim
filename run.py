from karim import LOCALHOST
import os, logging
import telegram
from karim import updater, BOT_TOKEN, URL, PORT

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == '__main__':
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
