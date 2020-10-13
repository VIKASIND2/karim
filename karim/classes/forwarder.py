from logging import exception
import jsonpickle
from telethon import client
import telethon
from telethon.errors.rpcerrorlist import FirstNameInvalidError, PeerFloodError
from telethon import utils

from karim.classes.persistence import persistence_decorator
from telethon.tl.functions.messages import *
from telethon.tl.types import InputPeerEmpty
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *
from karim.classes.callbacks import Callbacks
import math

class Forwarder(SessionManager):
    """Manages requests to the TelegramClient regarding the steps to scrape data from the Telegram API"""
    def __init__(self, method, chat_id, user_id, message_id, phone=None, password=None, code=None, phone_code_hash=None, code_tries=0, selected_ids=[], group_ids=None, group_titles=None, shown_ids=[], text=None, targets=[], rotate_size=6, first_index=0, last_index=None, page_index=1, pages=None, telethon_text=None):
        """
        groups: List of Dictionaries {id: title}
        selected_ids: Dictionary(id: title)
        shown_groups: Dictionary(id: title)
        """
        SessionManager.__init__(self, method=method, chat_id=chat_id, user_id=user_id, message_id=message_id, phone=phone, password=password, code=code, phone_code_hash=phone_code_hash, code_tries=code_tries)
        self.selected_ids = selected_ids
        self.group_ids = group_ids
        self.group_titles = group_titles
        self.shown_ids = shown_ids
        self.text = text
        self.rotate_size = rotate_size
        self.first_index = first_index
        self.last_index = last_index
        self.page_index = page_index
        self.pages = pages
        if last_index == None:
            self.last_index = self.first_index + self.rotate_size
        self.telethon_text = telethon_text


    def get_selection(self):
        """Return list()"""
        return self.selected_ids.copy()

    def get_groups(self, titles=False):
        """Return list()"""
        if titles:
            return self.group_titles.copy()
        return self.group_ids.copy()

    def get_groups_dict(self):
        groups = {}
        for index, group in enumerate(self.get_groups()):
            groups[group] = self.group_titles[index]
        return groups

    def get_shown(self):
        """Return list()"""
        return self.shown_ids.copy()

    def get_targets(self):
        """Return list()"""
        return self.targets.copy()

    def set_telethon_message(self, bot, message_date, client=None):
        print('forwarder.set_telethon_message()')
        if not client:
            client = self.create_client()
            client.connect()
        messages = client.get_messages(bot, limit=4, from_user=self.user_id)
        print('Messages size: ', len(messages), ' ', message_date)
        message = None
        for message in messages:
            print('Message: ', message.text, ' ', message.date)
            if message.date == message_date:
                message = message
                break
        try:
            self.telethon_text = message.text
        except:
            print('Message is None')
        return message  

    # Connects to Telegram API
    def scrape_dialogues(self, last_date=None, chunk_size=200):
        """
        Return a list of dicts of dialogues the client is connected to.
        """
        try:
            client = self.connect()
            group_titles = []
            group_ids = []
            chats = client.get_dialogs()
            for chat in chats:
                try:
                    if not chat.is_user:
                        group_ids.append(chat.id)
                        group_titles.append(chat.title)
                except:
                    print('Error')
                    continue
            client.disconnect()
            self.__set_groups(group_ids, group_titles)
            shown_ids = group_ids[self.first_index:self.last_index+1]
            self.__set_shown(shown_ids)
            return self.get_groups()
        except UnauthorizedError:
            raise UnauthorizedError
        except Exception:
            raise Exception

    @persistence_decorator
    def __set_groups(self, group_ids, group_titles):
        """Set group titles and ids"""
        self.pages = math.ceil(len(group_ids)//self.rotate_size)
        self.group_ids = group_ids
        self.group_titles = group_titles

    @persistence_decorator
    def __set_shown(self, shown_ids):
        """
        shown: List of group ids 
        """
        self.shown_ids = shown_ids

    @persistence_decorator
    def set_text(self, text):
        self.text = text
        return self.text

    # MANAGE MARKUP ROTATION AND SELECTIONS
    @persistence_decorator
    def add_selection(self, id):
        """id: group_id"""
        if str(id) in self.selected_ids:
            return Exception
        self.selected_ids.append(id)
        return self.selected_ids.copy()

    @persistence_decorator
    def remove_selection(self, id):
        """id: group_id"""
        self.selected_ids.remove(id)
        return self.selected_ids.copy()

    @persistence_decorator
    def rotate(self, direction):
        if direction == Callbacks.LEFT:
            if self.first_index == 0:
                self.page_index = self.pages
                self.first_index = len(self.group_ids) - self.rotate_size -1
                self.last_index = len(self.group_ids)
            elif self.page_index == 1:
                self.page_index == self.pages
                self.first_index = len(self.group_ids) - self.rotate_size-1
                self.last_index = len(self.group_ids) -1
            else:
                self.page_index -= 1
                self.first_index -= self.rotate_size +1
                self.last_index -= self.rotate_size +1

        elif direction == Callbacks.RIGHT:
            if self.last_index == len(self.group_ids):
                self.page_index = 1
                self.first_index = 0
                self.last_index = self.first_index + self.rotate_size
            elif self.page_index == self.pages-1:
                self.page_index += 1
                self.first_index = self.last_index
                self.last_index = len(self.group_ids)
            elif self.page_index == self.pages:
                self.page_index = 1
                self.first_index = 0
                self.last_index = self.first_index + self.rotate_size
            else:
                self.page_index += 1
                self.first_index += self.rotate_size+1
                self.last_index += self.rotate_size+1
        print('First Index: ', self.first_index)
        print('Last Index: ', self.last_index)
        shown = self.group_ids[self.first_index:self.last_index+1]
        self.__set_shown(shown)
        return self.get_shown()

    # GET PARTICIPANTS AND SEND MESSAG
    def load_targets(self, client=None):
        """Return a list of all members in a selection of chats
        :return: return list of chat ids
        :rtype: list<int>
        """
        targets = []
        groups = []
        try:
            if not client:
                client = self.create_client()
                client.connect()
            chats = client.get_dialogs()
            for chat in chats:
                if str(chat.id) in self.get_selection():
                    groups.append(chat)
            for group in groups:
                members = self.__scrape_participants(group, client)
                for member in members:
                    if member.id not in targets:
                        targets.append(member.id)
            if not client:
                client.disconnect()
            print('Targets: ', targets)
            return  targets
        except UnauthorizedError as unauth:
            raise unauth
        except Exception as exception:
            print('Exception in Forwarder.load_targets(): ', exception.args)

    # Connects to Telegram API
    def __scrape_participants(self, target_group, client):
        """
        Returns a list of all participants of a selected_ids group or channel
        """
        try:
            all_participants = client.get_participants(target_group, aggressive=True)
            return all_participants
        except UnauthorizedError as error:
            print('Error in retrievig participants: ', error)
            raise UnauthorizedError

    def send_message(self, target, client=None):
        if not client:
            client = self.create_client()
            client.connect()
        try:
            client.send_message(target, self.telethon_text)
        except Exception as error:
            print('Error in sending message ', error)
            raise error

    def send_messages(self, targets, client=None, context=None):
        if not client:
            client = self.create_client()
            client.connect()
        try:
            request = []
            for target in targets:
                request.append(SendMessageRequest(peer=target, message=self.telethon_text))
            client(request)
        except PeerFloodError as error:
            print('Peer Flood Limit reached when sending bulk messages - forwarder.send_messages(): ', error)
            raise error
        except Exception as error:
            print('Error in sending bulk messages - forwarder.send_messages(): ', error)
            raise error


            





    
            



       
