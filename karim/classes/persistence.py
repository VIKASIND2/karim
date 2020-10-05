from functools import wraps
import json
from karim import LOCALHOST, redis_connector

from telegram import update
from telethon.tl.functions.phone import DiscardCallRequest
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
        if LOCALHOST:
            # CODE RUNNING LOCALLY
            try:
                os.remove(
                "karim/bot/persistence/{}{}{}.json".format(self.method, self.user_id, self.chat_id))
            except FileNotFoundError:
                return self
        else:
            # CODE RUNNING ON SERVER
            redis_connector.delete('persistence:{}{}{}'.format(self.method, self.user_id, self.chat_id))

    def serialize(self):
        if LOCALHOST:
            # CODE RUNNING LOCALLY
            with open("karim/bot/persistence/{}{}{}.json".format(self.method, self.user_id, self.chat_id), "w") as write_file:
                objJSON = jsonpickle.encode(self, unpicklable=True)
                json.dump(objJSON, write_file, default=lambda o: o.__dict__, indent=4)
        else:
            # Code running on Heroku
            # Turn object into Json
            objJSON = jsonpickle.encode(self, unpicklable=True)
            # Turn Json into string
            objString = json.dumps(objJSON, indent=4)
            # Save string in Redis
            redis_connector.set('persistence:{}{}{}'.format(self.method, self.user_id, self.chat_id), objString)
        return self

    def deserialize(method, update):
        if LOCALHOST:
            # CODE RUNNING LOCALLY
            with open("karim/bot/persistence/{}{}{}.json".format(method, update.effective_chat.id, update.effective_chat.id), "r") as file:
                data = json.load(file)
                obj = jsonpickle.decode(data)
        else:
            # Code Running on Heroku
            # Get Redis String
            rstring = redis_connector.get("persistence:{}{}{}".format(method, update.effective_chat.id, update.effective_chat.id))
            # Turn into Object
            obj = jsonpickle.decode(rstring)
        return obj