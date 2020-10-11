import redis
from karim.classes.persistence import persistence_decorator
from karim.bot.commands import *
import asyncio
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PasswordHashInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError, PhoneNumberInvalidError, SessionPasswordNeededError, UnauthorizedError
from telethon.sessions import StringSession
from telethon.tl.types.auth import SentCode
from karim.secrets import secrets
from karim import LOCALHOST


class SessionManager(Persistence):
    """Used for persistance and passing of login information"""
    @persistence_decorator
    def __init__(self, method, chat_id, user_id, message_id, phone=None, password=None, code=None, phone_code_hash=None, code_tries=0):
        super().__init__(method=method, chat_id=chat_id, user_id=user_id, message_id=message_id)
        self.phone = phone
        self.password = password
        self.code = code
        self.phone_code_hash = phone_code_hash
        self.code_tries = code_tries

    def __str__(self):
        return 'SessionManager({}, {}, {}, {})'.format(self.phone, self.password, self.phone_code_hash)

    def __repr__(self):
        return 'SessionManager({}, {}, {}, {})'.format(self.phone, self.password, self.phone_code_hash)

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
        try:
            loop = asyncio.get_event_loop()
            loop.close()
        except:
            pass

    def create_client(self, user_id, sign_in=False):
        """Creates and returns a TelegramClient"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_id = secrets.get_var('API_ID')
        api_hash = secrets.get_var('API_HASH')

        if LOCALHOST:
            session = 'karim/bot/persistence/{}'.format(user_id)
        else:
            try:
                # Falling Back to RedisSession
                print('LOADING REDIS SESSION')
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                string = connector.get('session:{}'.format(self.user_id))
                print('SESSION STRING: ', string)
                if string:
                    # Session is stored in Redis
                    decoded_string = string.decode("utf-8") 
                    session = StringSession(decoded_string)
                else:
                    session = StringSession()
                connector.close()
            except Exception as error:
                # No Session Error
                print('Error in session_manager.create_client(): ', error)
                raise error
        client = TelegramClient(session, api_id, api_hash, loop=loop)
        print('TELEGRAM CLIENT WITH SESSION: ', client)
        return client

    @persistence_decorator
    def request_code(self):
        client = self.create_client(self.user_id)
        client.connect()
        print('SENT CODE TO ', self.phone)
        sent_code: SentCode = client.send_code_request(self.phone)
        client.sign_in(phone=self.phone, phone_code_hash=self.phone_code_hash)
        print('SENT CODE REQUEST! ', sent_code)
        self.phone_code_hash = sent_code.phone_code_hash
        self.code_tries += 1
        client.disconnect()
        return sent_code


    def sign_in(self, client=None, password=False):
        """
        Sign into the Telegram Client using the user's session file - tied thanks to the user id
        :returns: TelegramClient (if user has access) | PhoneCodeInvalidError (if security code is wrong)
        """
        try:
            if not client:
                client = self.create_client(self.user_id, sign_in=True)
            client.connect()
            if not password:
                client.sign_in(phone=self.phone, code=self.code, phone_code_hash=self.phone_code_hash)

            else:
                client.sign_in(phone=self.phone, password=self.password)
            # Save session in database
            result = client.is_user_authorized()
            # Save Session in Redis
            if not LOCALHOST:
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                session_string = client.session.save()
                connector.set('session:{}'.format(self.user_id), session_string)
                connector.close()
                print('SIGNED IN WITH STRING: ', client.session)
            client.disconnect()
            return result
        except UnauthorizedError as unauthorized:
            print('Exception when Signing In: ', unauthorized.args)
            raise unauthorized
        except PhoneCodeExpiredError as code_expired:
            print('Exception when Signing In: ', code_expired.args)
            raise code_expired
        except PhoneCodeInvalidError as code_invalid:
            print('Exception when Signing In: ', code_invalid.args)
            raise code_invalid
        except PhoneNumberInvalidError as phone_invalid:
            print('Exception when Signing In: ', phone_invalid.args)
            raise phone_invalid
        except PasswordHashInvalidError as password_error:
            print('Exception when Signing In: ', password_error.args)
            raise password_error
        except Exception as exception:
            print('Exception when Signing In: ', exception.args)
            raise exception

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
            try: 
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                connector.delete('session:{}'.format(self.user_id))
                connector.close()
            except Exception as error:
                print('Error in session_manager.sign_out(): ', error)
        return result 