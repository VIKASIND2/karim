from karim.bot.commands import *
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, FloodWaitError, UnauthorizedError
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

    def set_phone(self, phone):
        self.phone = phone

    def set_password(self, password):
        self.password = password

    def set_code(self, code):
        self.code = code

    def create_client(self, user_id):
        """Creates and returns a TelegramClient"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_id = secrets.get_var('API_ID')
        api_hash = secrets.get_var('API_HASH')
        client = TelegramClient('karim/bot/sessions/{}'.format(user_id), api_id, api_hash, loop=loop)
        return client

    def request_code(self):
        #try:
        client = self.create_client(self.user_id)
        client.connect()
        sent_code: SentCode = client.send_code_request(self.phone, force_sms=True)
        self.phone_code_hash = sent_code.phone_code_hash
        return None
        #except FloodWaitError:
        #    return FloodWaitError

    def sign_in(self, client=None):
        """
        Sign into the Telegram Client using the user's session file - tied thanks to the user id
        :returns: TelegramClient (if user has access) | PhoneCodeInvalidError (if security code is wrong)
        """
        try:
            if not client:
                client = self.create_client(self.user_id)
            client.connect()
            client.sign_in(phone=self.phone, code=self.code, password=self.password, phone_code_hash=self.phone_code_hash)
            return client
        except PhoneCodeInvalidError:
            print('Phone Code is invalid')
            return PhoneCodeInvalidError

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
            if not result:
                return UnauthorizedError
            return None
        except:
            return Exception

    def connect(self, client=None):
        """
        Connect to the Telegram Client
        :returns: TelegramClient (if user has access) | UnauthorizedError if user does not have access | Exception if an error occured
        """
        try:
            if not client:
                client = self.create_client(self.user_id)
            client.connect()
            result = client.is_user_authorized()
            if not result:
                # User is not logged in
                raise UnauthorizedError
            else:
                # User is logged in, return client
                return client
        except:
            # Error occured
            raise Exception