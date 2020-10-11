import json
from logging import exception

from teleredis.teleredis import RedisSession

from karim import LOCALHOST
from telegram import update
from telethon.sessions import StringSession
import os, jsonpickle, redis

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
    
    def __init__(self, method, chat_id, user_id, message_id=None):
        self.method = method
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = message_id


    @persistence_decorator
    def set_message(self, message_id):
        self.message_id = message_id
        return self.message_id

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
            try:
                connector: RedisSession = redis.from_url(os.environ.get('REDIS_URL'))
                connector.delete('persistence:{}{}{}'.format(self.method, self.user_id, self.chat_id))
                connector.feed_session()
                connector.close()
            except Exception as error:
                print('Error in persistence.discard(): ', error)

    def serialize(self):
        if LOCALHOST:
            # CODE RUNNING LOCALLY
            obj_dict = self.__dict__
            with open("karim/bot/persistence/{}{}{}.json".format(self.method, self.user_id, self.chat_id), "w") as write_file:
                 json.dump(obj_dict, write_file, indent=4)
        else:
            # Code running on Heroku
            # Turn object into dict
            obj_dict = self.__dict__
            for key in obj_dict.keys():
                if obj_dict.get(key) is None:
                    obj_dict[key] = -1
            try:
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                obj_string = json.dumps(obj_dict)
                connector.set('persistence:{}{}{}'.format(self.method, self.user_id, self.chat_id), obj_string)
                print('Serializng: ', obj_string)
                connector.feed_session()
                connector.close()
            except Exception as error:
                print('Error in persistence.serialize(): ', error)
        return self

    def deserialize(method, update):
        if LOCALHOST:
            # CODE RUNNING LOCALLY
            with open("karim/bot/persistence/{}{}{}.json".format(method, update.effective_chat.id, update.effective_chat.id)) as file:
                return json.load(file)
        else:
            # Code Running on Heroku
            # Get Redis String
            try:
                connector = redis.from_url(os.environ.get('REDIS_URL'))
                obj_bytes = connector.get("persistence:{}{}{}".format(method, update.effective_chat.id, update.effective_chat.id))
                connector.close()
                obj_string = json.loads(obj_bytes)
                # Turn into Object
                # Class is Persistence
                obj_dict = dict(obj_string)
                print('Deserialized: ', obj_dict)
                return obj_string
            except Exception as error:
                print('Error in persistence.deserialzie(): ', error)
            