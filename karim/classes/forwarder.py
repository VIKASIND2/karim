from itertools import groupby
from jinja2.environment import create_cache

from telethon import client
from karim.classes.persistence import persistence_decorator
from logging import root
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *
import math

class Forwarder(SessionManager):
    """Manages requests to the TelegramClient regarding the steps to scrape data from the Telegram API"""
    def __init__(self, update, last_index=0):
        """
        groups: List of Dictionaries {id: title}
        selected: Dictionary(id: title)
        shown_groups: Dictionary(id: title)
        """
        SessionManager.__init__(self, update, self.FORWARDER)
        self.selected = {}
        self.groups = None
        self.shown_groups = {}
        self.text = None
        self.targets = []
        self.rotate_size = 6
        self.first_index = 0
        self.last_index = self.first_index + self.rotate_size
        self.page_index = 1
        self.pages = None

    def get_selection(self):
        return self.selected.copy()

    def get_groups(self):
        return self.groups.copy()

    def get_shown(self):
        return self.shown_groups.copy()

    def get_targets(self):
        return self.targets.copy()

    # Connects to Telegram API
    def scrape_dialogues(self, last_date=None, chunk_size=200):
        """
        Return a list of dicts of dialogues the client is connected to.
        """
        try:
            client = self.connect()
            groups = []
            chats = client.get_dialogs()
            for chat in chats:
                try:
                    if not chat.is_user:
                        groups.append({chat.id: chat.title})
                except:
                    print('Error')
                    continue
            client.disconnect()
            self.__set_groups(groups)
            shown = groups[self.first_index:self.last_index+1]
            self.__set_shown(shown)
            return self.get_groups()
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise Exception

    @persistence_decorator
    def __set_groups(self, groups):
        self.pages = math.ceil(len(groups)//self.rotate_size)
        self.groups = groups

    @persistence_decorator
    def __set_shown(self, shown):
        """
        shown: List of Dictionaries (id: title)
        """
        updated_shown = {}
        for item in shown:
            updated_shown[list(item.keys())[0]] = list(item.values())[0]
        self.shown_groups = updated_shown

    @persistence_decorator
    def set_text(self, text):
        self.text = text
        return self.text

    # MANAGE MARKUP ROTATION AND SELECTIONS
    @persistence_decorator
    def add_selection(self, id):
        if str(Callbacks.UNSELECT+id) in self.selected:
            return
        self.selected[id] = self.shown_groups[id]
        return self.selected.copy()

    @persistence_decorator
    def remove_selection(self, id):
        del self.selected[id]
        return self.selected.copy()

    @persistence_decorator
    def rotate(self, direction):
        if direction == Callbacks.LEFT:
            if self.first_index == 0:
                self.page_index = self.pages
                self.first_index = len(self.groups) - self.rotate_size
                self.last_index = len(self.groups)-1
            elif self.first_index - self.rotate_size < 0:
                self.page_index -= 1
                self.last_index = self.first_index
                self.first_index = 0
            else:
                self.page_index -= 1
                self.first_index -= self.rotate_size +1
                self.last_index -= self.rotate_size +1

        elif direction == Callbacks.RIGHT:
            if self.last_index == len(self.groups) -1:
                self.page_index = 1
                self.first_index = 0
                self.last_index = self.first_index + self.rotate_size
            elif self.last_index + self.rotate_size > len(self.groups):
                self.page_index += 1
                self.first_index = self.last_index
                self.last_index = len(self.groups)
            else:
                self.page_index += 1
                self.first_index += self.rotate_size+1
                self.last_index += self.rotate_size+1
        shown = self.groups[self.first_index:self.last_index+1]
        self.__set_shown(shown)
        return self.get_shown()

    # GET PARTICIPANTS AND SEND MESSAGE
    def send(self):
        count = 0
        fail = 0
        client = self.create_client(self.user_id)
        try:
            # LOAD CHATS
            client = self.connect(client)
            groups = []
            chats = client.get_dialogs()
            for chat in chats:
                if str(chat.id) in self.get_selection():
                    groups.append(chat)
                    print(chat.title)
            # LOAD & SCRAPE TARGETS
            targets = self.__load_targets(client, groups)
            # SEND MESSAGES
            for target in targets:
                try:
                    client.send_message(target, self.text.text_markdown)
                    count += 1
                except:
                    fail += 1
                    continue
            client.disconnect()
            return [count, fail]
        except UnauthorizedError:
            raise UnauthorizedError
        

    def __load_targets(self, client, groups):
        targets = []
        for group in groups:
            members = self.__scrape_participants(group, client)
            for member in members:
                if member.id not in targets:
                    targets.append(member)
        self.targets = targets
        return  self.targets

    # Connects to Telegram API
    def __scrape_participants(self, target_group, client):
        """
        Returns a list of all participants of a selected group or channel
        """
        try:
            all_participants = client.get_participants(target_group, aggressive=True)
            print(all_participants)
            return all_participants
        except UnauthorizedError:
            raise UnauthorizedError
    
            


            





    
            



       
