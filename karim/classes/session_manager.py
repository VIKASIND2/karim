from karim.classes.teleredis import RedisSession
from karim.classes.persistence import persistence_decorator
from karim.bot.commands import *
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError, SessionPasswordNeededError, UnauthorizedError
from telethon.tl.types.auth import SentCode
from karim.secrets import secrets
from karim import LOCALHOST, redis_connector


class SessionManager(Persistence):
    """Used for persistance and passing of login information"""
    @persistence_decorator
    def __init__(self, update, method):
        super().__init__(update, method)
        self.phone = None
        self.password = None
        self.code = None
        self.phone_code_hash = None
        self.code_tries = 0

    @persistence_decorator
    def set_phone(self, phone):
        self.phone = phone.replace(' ', '')
        self.serialize()

    @persistence_decorator
    def set_password(self, password):
        self.password = password
        self.serialize()

    @persistence_decorator
    def set_code(self, code):
        self.code = code.replace('.', '')
        self.serialize()

    def discard(self):
        super().discard()
        loop = asyncio.get_event_loop()
        loop.close()

    def create_client(self, user_id):
        """Creates and returns a TelegramClient"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_id = secrets.get_var('API_ID')
        api_hash = secrets.get_var('API_HASH')

        if LOCALHOST:
            session = 'karim/bot/persistence/{}'.format(user_id)
        else:
            session = RedisSession(user_id, redis_connector)
        client = TelegramClient(session, api_id, api_hash, loop=loop)
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
        try:
            if not client:
                client = self.create_client(self.user_id)
                client.connect()
                result = client.is_user_authorized()
                client.disconnect()
                return result
        except: 
            return Exception
        
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
        if LOCALHOST:
            try:
                os.remove('karim/bot/persistence/{}.session'.format(self.user_id))
            except: pass 
        else: 
            print('Should delete Redis Session...')
        return result      