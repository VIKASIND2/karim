from telethon.tl.functions.auth import CancelCodeRequest
from karim.classes.persistence import persistence_decorator
from karim.bot.commands import *
from karim.secrets import secrets
from karim import LOCALHOST

import asyncio, redis

from telethon.sync import TelegramClient
from telethon import connection
from telethon.errors.rpcerrorlist import *
from telethon import functions, types
from telethon.sessions import StringSession
from telethon.tl.types.auth import SentCode


class SessionManager(Persistence):
    """Used for persistance and passing of login information"""
    @persistence_decorator
    def __init__(self, method, chat_id, user_id, message_id):
        super().__init__(method=method, chat_id=chat_id, user_id=user_id, message_id=message_id)
        self.phone = None
        self.password = None
        self.code = None
        self.phone_code_hash = None
        self.code_tries = None

    def __str__(self):
        return 'SessionManager({}, {}, {})'.format(self.phone, self.password, self.phone_code_hash)

    def __repr__(self):
        return 'SessionManager({}, {}, {})'.format(self.phone, self.password, self.phone_code_hash)

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

    def create_client(self):
        """Creates and returns a TelegramClient"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        api_id = secrets.get_var('API_ID')
        api_hash = secrets.get_var('API_HASH')
        # TODO
        # proxy=(socks.SOCKS5, '127.0.0.1', 4444)

        if LOCALHOST:
            session = 'karim/bot/persistence/{}'.format(self.user_id)
        else:
            session_string = os.environ.get('session:{}'.format(self.user_id))
            if not session_string:
                try:
                    # Falling Back to RedisSession
                    print('LOADING REDIS SESSION')
                    connector = redis.from_url(os.environ.get('REDIS_URL'))
                    string = connector.get('session:{}'.format(self.user_id))
                    print('SESSION STRING OUTPUTTED')
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
            else:
                try:
                    session = StringSession(session_string)
                except Exception as error:
                    print('Error in session_manager.create_client(): ', error)
                    raise error
        try:
            client = TelegramClient(session, api_id, api_hash, loop=loop) #proxy = proxy
        except Exception as error:
            print('Error in session_manager.create_client(): ', error)
            raise error
        print('TELEGRAM CLIENT WITH SESSION CREATED')
        return client

    @persistence_decorator
    def request_code(self):
        client = self.create_client()
        client.connect()
        print('SENT CODE TO PHONE')
        #if not request_again:
        try:
            sent_code = client(functions.auth.SendCodeRequest(phone_number=self.phone, api_id=int(secrets.get_var('API_ID')), api_hash=secrets.get_var('API_HASH'), settings=types.CodeSettings(allow_flashcall=True, current_number=True, allow_app_hash=True)))
        except PhoneNumberFloodError as error:
            print('Error in session_manager.request_code(): ', error)
            raise error
        except PhonePasswordFloodError as error:
            print('Error in session_manager.request_code(): ', error)
            raise error
        except PhonePasswordProtectedError as error:
            print('Error in session_manager.request_code(): ', error)
            raise error
        except Exception as error:
            print('Error in session_manager.request_code(): ', error)
            raise error
        """ else:
            try:
                sent_code = client(ResendCodeRequest(self.phone, self.phone_code_hash))
            except PhoneNumberInvalidError as error:
                print('Error in session_manager.request_code(): ', error)
                raise error
            except Exception as error:
                print('Error in session_manager.request_code(): ', error)
                raise error """
        print('SENT CODE REQUEST!')
        self.phone_code_hash = sent_code.phone_code_hash
        self.code_tries += 1
        client.disconnect()
        return sent_code


    def cancel_code_request(self, client=None):
        if not client:
            client = self.create_client()
        try:
            client(CancelCodeRequest(self.phone, self.phone_code_hash))
        except PhoneNumberInvalidError as error:
            print('Error in session_manager.cancel_code_request(): ', error)
            raise error
        except Exception as error:
            print('Error in session_manager.cancel_code_request(): ', error)
            raise error


    def sign_in(self, client=None, password=False):
        """
        Sign into the Telegram Client using the user's session file - tied thanks to the user id
        :returns: TelegramClient (if user has access) | PhoneCodeInvalidError (if security code is wrong)
        """
        try:
            if not client:
                client = self.create_client()
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
                os.environ['session:{}'.format(self.user_id)] =  session_string
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
                client = self.create_client()
                client.connect()
                result = client.is_user_authorized()
                client.disconnect()
                return result
        except Exception as error: 
            print('Error in checking the connection: ', error.args)
            return error
        
    def connect(self, client=None):
        """
        Connect to the Telegram Client
        :returns: TelegramClient (if user has access) | UnauthorizedError if user does not have access | Exception if an error occured
        """
        if not client:
            client = self.create_client()
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
            client = self.create_client()
            client.connect()
        result = client.log_out()
        client.disconnect()
        if LOCALHOST:
            try:
                os.remove('karim/bot/persistence/{}.session'.format(self.user_id))
            except: pass 
        else: 
            print('Should delete Redis Session...')
            session_string = os.environ.get('session:{}'.format(self.user_id))
            if not session_string:
                try: 
                    connector = redis.from_url(os.environ.get('REDIS_URL'))
                    connector.delete('session:{}'.format(self.user_id))
                    connector.close()
                except Exception as error:
                    print('Error in session_manager.sign_out(): ', error)
            else:
                try:
                    del os.environ['session:{}'.format(self.user_id)]
                except Exception as error:
                    print('Error in deleting env var: ', error)
                    pass
        return result 