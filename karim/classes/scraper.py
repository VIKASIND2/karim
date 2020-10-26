from karim.classes.persistence import Persistence, persistence_decorator


class Scraper(Persistence):
    """
    Manage persistence within the Scrape Followers conversation.
    Extends the Persistence class
    """
    def __init__(self, method, chat_id: int or str, user_id: int or str, message_id: int or str):
        super().__init__(method, chat_id, user_id, message_id)
        self.name = None
        self.count = None
        self.target = None

    @persistence_decorator
    def set_name(self, name:str):
        self.name = name

    @persistence_decorator
    def set_count(self, count:int):
        self.count = count

    @persistence_decorator
    def set_target(self, target:str):
        self.target = target

    def get_count(self):
        return self.count

    def get_target(self):
        return self.target