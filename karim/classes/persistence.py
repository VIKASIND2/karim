from functools import wraps
import json

from telegram import update
from telethon.tl.functions.phone import DiscardCallRequest
from karim.bot import persistence
import os, jsonpickle

def persistence_decorator(func):
    def wrapper(self, *args, **kw):
        # Call function
        print('Pikling: ', type(self))
        output = func(self, *args, **kw)
        # Post Processing
        self.serialize()
        return output
    return wrapper

class Persistence(object):
    """Class to save objects in pickle files for bot Conversation Persistance"""
    SIGNIN = 'signin'
    SIGNOUT = 'signout'
    ACCOUNT = 'account'
    FORWARDER = 'forwarder'
    
    def __init__(self, update, method):
        self.method = method
        self.chat_id = update.effective_chat.id
        self.user_id = update.effective_user.id
        self.update = None
        self.message = None

    def get_obj(self):
        return self.obj

    @persistence_decorator
    def set_update(self, update):
        self.update = update
        self.serialize()
        return self.update

    @persistence_decorator
    def set_message(self, message):
        self.message = message
        self.serialize()
        return self.message

    def discard(self):
        try:
            os.remove(
            "karim/bot/persistence/{}{}{}.json".format(self.method, self.user_id, self.chat_id))
        except FileNotFoundError:
            return self

    def serialize(self):
        with open("karim/bot/persistence/{}{}{}.json".format(self.method, self.user_id, self.chat_id), "w") as write_file:
            objJSON = jsonpickle.encode(self, unpicklable=True)
            json.dump(objJSON, write_file, default=lambda o: o.__dict__, indent=4)
        return self

    def deserialize(method, update):
        with open("karim/bot/persistence/{}{}{}.json".format(method, update.effective_chat.id, update.effective_chat.id), "r") as file:
            data = json.load(file)
            obj = jsonpickle.decode(data)
        return obj