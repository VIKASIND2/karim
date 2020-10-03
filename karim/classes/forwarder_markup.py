from karim.bot.commands import *

class CreateMarkup():
    """
    Class describing a Reply Markup Menu.
    """
    def __init__(self, titles=[], callbacks=[], cols=1):
        self.titles = titles
        self.callbacks = callbacks
        self.cols = 1
        self.keyboard = []
        self.markup = None

    def set_titels(self, titles):
        self.titles = titles
        return self.titles.copy()

    def set_callbacks(self, callbacks):
        self.callbacks = callbacks
        return self.callbacks.copy()

    def set_cols(self, cols):
        self.cols = cols
        return cols

    def set_keyboard(self, keyboard):
        self.keyboard = keyboard
        return self.keyboard.copy()

    def set_markup(self, markup):
        self.markup = markup

    def create_keyboard(self):
        keyboard = []
        index = 0
        row = []
        for title in self.titles:
            keyboard_button = InlineKeyboardButton(
                title, callback_data=self.callbacks[index])
            if len(row) < self.cols:
                row.append(keyboard_button)
            else:
                keyboard.append(row)
                row = []
                row.append(keyboard_button)
            index += 1
        if row != "":
            keyboard.append(row)
        return keyboard

    def create_markup(self):
        return InlineKeyboardMarkup(self.keyboard)

class MarkupDivider(CreateMarkup):
    """An InlineMarkupButton with no attached callback used to divide sections of the ForwarderMarkup"""
    def __init__(self, title):
        CreateMarkup.__init__(self, [title], [Callbacks.NONE], cols=1)
        self.title = title


class ForwarderMarkup(CreateMarkup):
    def __init__(self, forwarder: Forwarder):
        self.selected = forwarder.get_selection()
        self.shown_options = None


