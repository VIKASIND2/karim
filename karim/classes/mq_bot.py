from karim.secrets import secrets
import telegram.bot
from telegram.ext import messagequeue as mq 

class MQBot(telegram.bot.Bot):
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()
    
    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_queued_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)

    def report_error(self, error=None, send_screenshot=False, screenshot_name=''):
        string = str(secrets.get_var('DEVS')).replace('[', '')
        string = string.replace(']', '')
        string = string.replace(' ', '')
        devs = list(string.split(','))
        for dev in devs:
            if send_screenshot:
                self.send_photo(chat_id=int(dev), photo=open('{}.png'.format(screenshot_name), 'rb'))
            self.send_message(chat_id=int(dev), text='There was an error with the Karim Luman bot: \n{}'.format(error))