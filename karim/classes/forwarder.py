from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *

class Forwarder(SessionManager):
    """
    Manages requests to the TelegramClient regarding the steps to scrape data from the Telegram API
    """
    def __init__(self, update):
        Persistence.__init__(self, update, self.FORWARDER)
        SessionManager.__init__(self, update)
        self.selection = []
        self.groups = None
        self.message = None
        self.participants = []

    # Connects to Telegram API
    def get_dialogues(self, last_date=None, chunk_size=200):
        """
        Return a list of dialogues the client is connected to.
        """
        try:
            client = self.connect()
            chats = []
            groups=[]
            
            result = client(GetDialogsRequest(
                        offset_date=last_date,
                        offset_id=0,
                        offset_peer=InputPeerEmpty(),
                        limit=chunk_size,
                        hash = 0
                    ))
            chats.extend(result.chats)
            
            for chat in chats:
                try:
                    if not chat.is_user:
                        groups.append(chat)
                except:
                    continue
            client.disconnect()
            return groups
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise Exception

    # Connects to Telegram API
    def get_participants(self, target_group):
            """
            Returns a list of all participants of a selected group or channel
            """
            try:
                client = self.connect()
                all_participants = client.get_participants(target_group, aggressive=True)
                client.disconnect()
                return all_participants
            except UnauthorizedError:
                raise UnauthorizedError
            except Exception:
                raise Exception
        
    def get_selection(self):
        return self.selection.copy()
    
    def set_groups(self, groups):
        self.groups = groups

    def add_selection(self, selected):
        self.selection.append(selected)
        return self.selection.copy()

    def remove_selection(self, selected):
        self.selection.remove(selected)
        return self.selection.copy()

    def add_participants(self, participants):
        self.participants.extend(participants)
        return self.participants.copy()

    
            



       
