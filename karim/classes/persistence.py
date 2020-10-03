from karim.bot import persistence
import pickle, os, joblib

class Persistence(object):
    """Class to save objects in pickle files for bot Conversation Persistance"""
    ATTEMPT = 'attempt'
    FORWARDER = 'forwarder'
    
    def __init__(self, update, method):
        self.method = method
        self.chat_id = update.effective_chat.id
        self.user_id = update.effective_user.id
        self.update = None
        self.message = None
        self.dump_pkl()

    def get_obj(self):
        return self.obj

    def set_update(self, update):
        self.update = update
        self.dump_pkl()
        return self

    def set_message(self, message):
        self.message = message
        self.dump_pkl()
        return self

    def dump_pkl(self):
        path = r'karim\bot\persistence'
        if not os.path.exists(path):
            os.makedirs(path)
        joblib.dump(
            self, "karim/bot/persistence/{}_{}_{}.pkl".format(self.method, self.chat_id, self.user_id))
        return self

    def delete_pkl(self):
        os.remove(
            "karim/bot/persistence/{}_{}_{}.pkl".format(self.method, self.chat_id, self.user_id))
        return self

    def load_pkl(method, update):
        try:
            obj = joblib.load(
                "karim/bot/persistence/{}_{}_{}.pkl".format(method, update.effective_chat.id, update.effective_user.id))
            return obj
        except:
            return None