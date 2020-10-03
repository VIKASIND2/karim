from karim.bot.commands import *
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError, SessionPasswordNeededError, UnauthorizedError
from telethon.tl.types.auth import SentCode
from karim.secrets import secrets


class SessionManager(Persistence):
    """Used for persistance and passing of login information"""
    def __init__(self, update):
        Persistence.__init__(self, update, self.ATTEMPT)
        self.user_id = update.effective_user.id
        self.phone = None
        self.password = None
        self.code = None
        self.phone_code_hash = None
        self.code_tries = 0

    def set_phone(self, phone):
        self.phone = phone

    def set_password(self, password):
        self.password = password

    def set_code(self, code):
        self.code = code.replace('.', '')

    def create_client(self, user_id):
        """Creates and returns a TelegramClient"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_id = secrets.get_var('API_ID')
        api_hash = secrets.get_var('API_HASH')
        client = TelegramClient('karim/bot/sessions/{}'.format(user_id), api_id, api_hash, loop=loop)
        return client

    def request_code(self):
        client = self.create_client(self.user_id)
        client.connect()
        sent_code: SentCode = client.send_code_request(self.phone)
        self.phone_code_hash = sent_code.phone_code_hash
        self.code_tries += 1
        client.disconnect()
        return None

    def sign_in(self, client=None, password=False):
        """
        Sign into the Telegram Client using the user's session file - tied thanks to the user id
        :returns: TelegramClient (if user has access) | PhoneCodeInvalidError (if security code is wrong)
        """
        if not client:
            client = self.create_client(self.user_id)
        client.connect()
        if not password:
            client.sign_in(phone=self.phone, code=self.code, phone_code_hash=self.phone_code_hash)
        else:
            client.sign_in(phone=self.phone, password=self.password)
        client.disconnect()

    def check_connection(self, client=None):
        """
        Check if the session has access to the client user account
        :returns: None if user has access | UnauthorizedError if user does not have access | Exception if an error occured
        """
        if not client:
            client = self.create_client(self.user_id)
        client.connect()
        result = client.is_user_authorized()
        client.disconnect()
        return result

    def connect(self, client=None):
        """
        Connect to the Telegram Client
        :returns: TelegramClient (if user has access) | UnauthorizedError if user does not have access | Exception if an error occured
        """
        if not client:
                client = self.create_client(self.user_id)
        client.connect()
        result = client.is_user_authorized()
        if not result:
            # User is not logged in
            client.disconnect()
            raise UnauthorizedError
        else:
            # User is logged in, return client
            return client

    def sign_out(self, client=None):
        if not client:
            client = self.create_client(self.user_id)
            client.connect()
        result = client.log_out()
        client.disconnect()
        try: os.remove('karim/bot/sessions/{}.session'.format(self.user_id)) 
        except: pass
        return result      