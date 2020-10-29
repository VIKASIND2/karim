from karim.classes.persistence import persistence_decorator
from karim.bot.commands import *
import os, redis

class InstaSession(Persistence):
    def __init__(self, chat_id, user_id, message_id=None):
        super().__init__(Persistence.INSTASESSION, chat_id, user_id, message_id)
        self.username = None
        self.password = None
        self.security_code = None
        self.code_request = 0

    @persistence_decorator
    def set_username(self, username):
        self.username = username

    @persistence_decorator
    def set_password(self, password):
        self.password = password

    @persistence_decorator
    def set_scode(self, scode):
        self.security_code = scode

    @persistence_decorator
    def increment_code_request(self):
        self.code_request += 1

    def save_creds(self):
        """
        Store working instagram credentials (username and password) into 
        """
        connector = redis.from_url(os.environ.get('REDIS_URL'))
        connector.delete('instacreds:{}'.format(self.user_id))
        connector.hmset('instacreds:{}'.format(self.user_id), {self.username: self.password})
        connector.close()

    def get_creds(self):
        connector = redis.from_url(os.environ.get('REDIS_URL'))
        creds:dict = connector.hgetall('instacreds:{}'.format(self.user_id))
        connector.close()
        if not creds or list(creds.keys()) == []:
            # No credentials
            return False
        else:
            print(creds)
            self.set_username(list(creds.keys())[0].decode('utf-8'))
            print(self.username)
            self.set_password(creds.get(bytes(self.username, encoding='utf8')).decode('utf-8'))
            return True
