from karim.bot.commands import *

class InstaSession(Persistence):
    def __init__(self, chat_id, user_id, message_id=None):
        super().__init__(Persistence.INSTASESSION, chat_id, user_id, message_id)
        username = None
        password = None
        security_code = None

    def set_username(self, username):
        self.username = username


    def set_password(self, password):
        self.password = password

    
    def set_scode(self, scode):
        self.security_code = scode