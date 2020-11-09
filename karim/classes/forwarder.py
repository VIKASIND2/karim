from telethon.errors.rpcerrorlist import ChatAdminRequiredError, FirstNameInvalidError, PeerFloodError
from telethon import utils
from telethon.tl.functions.messages import *
from telethon.errors.rpcbaseerrors import UnauthorizedError
from karim.bot.commands import *
from karim.classes.callbacks import Callbacks
from karim import queue
from karim.classes.persistence import persistence_decorator
import math, time

class Forwarder(SessionManager):
    def __init__(self, method, chat_id, user_id, message_id):
        SessionManager.__init__(self, method=method, chat_id=chat_id, user_id=user_id, message_id=message_id)
        self.mode = None
        self.text = None
        # Specific to Telegram mode
        self.selected_ids = []
        self.group_ids = []
        self.group_titles = []
        self.shown_ids = []
        self.rotate_size = 6
        self.first_index = 0
        self.last_index = 6
        self.page_index = 1
        self.pages = None
        self.telethon_text = None
        # Specific to Newsletter
        self.subscribers = None
        # Specific to IG
        self.users = []
        self.count = None
        self.completed = None


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

    def get_users(self):
        """Return IG Users usernames"""
        return self.users.copy()

    def get_mode(self):
        """Return forwarder mode"""
        return self.mode

    def get_completed_dm(self):
        """
        Get the number of completed `send_dm_job` tasks

        Returns:
            int: Number of completed `send_dm_job` tasks
        """
        if self.completed == None:
            return 0
        return self.completed

    def set_telethon_message(self, bot, message_date, client=None):
        print('forwarder.set_telethon_message()')
        if not client:
            client = self.create_client()
            client.connect()
        messages = client.get_messages(bot, limit=4, from_user=self.user_id)
        message = None
        for message in messages:
            if message.date == message_date:
                message = message
                break
        try:
            self.telethon_text = message.text
        except:
            print('Message is None')
        client.disconnect()
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
                    if not chat.is_user and chat.id not in group_ids:
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

    @persistence_decorator
    def set_count(self, count):
        self.count = count
        return self.count

    @persistence_decorator
    def set_users(self, users:list):
        """
        Set users (instagram usernames) to send the IG DMs to

        :param users: List of instagram usernames
        :type users: list
        :return: Returns the saved users list
        :rtype: list
        """
        self.users = users
        return self.users.copy()

    @persistence_decorator
    def set_mode(self, mode):
        self.mode = mode
        return self.mode

    @persistence_decorator
    def set_completed_dm(self, completed):
        if self.completed == None:
            self.completed = 1
        else:
            self.completed += 1
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
                try:
                    members = self.__scrape_participants(group, client)
                    for member in members:
                        if member.username not in targets and member.id != self.user_id:
                            if member.username == None:
                                targets.append(member.id)
                            else:
                                targets.append(member.username)
                except ChatAdminRequiredError as error:
                    continue
            if not client:
                client.disconnect()
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
        except ChatAdminRequiredError as error:
            print('User does not have permission to get members list: ', error)
            raise ChatAdminRequiredError
        except UnauthorizedError as error:
            print('Error in retrievig participants: ', error)
            raise UnauthorizedError


        
            





    
            



       
