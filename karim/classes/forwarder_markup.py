from karim.classes.callbacks import Callbacks
from karim.bot.commands import *

class CreateMarkup():
    """
    Class describing a Reply Markup Menu.
    """
    def __init__(self, items, cols=1):
        self.items = items
        self.titles = list(items.values())
        self.callbacks = list(items.keys())
        self.cols = cols
        self.keyboard = self.create_keyboard()
        self.markup = None

    def set_titel(self, titles):
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
        CreateMarkup.__init__(self, {Callbacks.NONE: title}, cols=1)


class ForwarderMarkup():
    CHECKBOX = '(•) '
    def __init__(self, forwarder: Forwarder):
        self.groups = forwarder.get_groups_dict()
        self.selected_div = 'SELECTED GROUPS:'
        self.selected = self.__format_dicts(forwarder.get_selection(), Callbacks.UNSELECT)
        self.shown_div = 'SELECT BELOW [{}/{}]'.format(forwarder.page_index, forwarder.pages)
        self.shown_selection = self.__format_dicts(forwarder.get_shown(), Callbacks.SELECT, forwarder.get_selection())
        self.arrows = {Callbacks.LEFT: '<', Callbacks.RIGHT: '>'}
        self.options = {Callbacks.CANCEL: 'Cancel', Callbacks.DONE: 'Done'}
        self.set_keyboard()

    def __format_dicts(self, groups, callback, selected=None):
        updated_dict = {}
        for group in groups:
            if callback is Callbacks.SELECT:
                if int(group) in selected or str(group) in selected:
                    updated_dict[callback+str(group)] = self.CHECKBOX+self.groups[group]
                else:
                    updated_dict[callback+str(group)] = self.groups[group]
            else:
                updated_dict[callback+str(group)] = self.groups[int(group)]
        return updated_dict

    def set_keyboard(self):
        selected_div_kb = MarkupDivider(self.selected_div).create_keyboard()
        selected_kb = CreateMarkup(self.selected, cols=2).create_keyboard()
        shown_div_kb = MarkupDivider(self.shown_div).create_keyboard()
        shown_selection_kb = CreateMarkup(self.shown_selection).create_keyboard()
        arrows_kb = CreateMarkup(self.arrows, cols=2).create_keyboard()
        options_kb = CreateMarkup(self.options, cols=2).create_keyboard()

        keyboard = [selected_div_kb[0]]
        for row in selected_kb:
            keyboard.append(row)
        keyboard.append(shown_div_kb[0])
        for row in shown_selection_kb:
            keyboard.append(row)
        keyboard.append(arrows_kb[0])
        keyboard.append(options_kb[0])
        self.keyboard = keyboard
        return keyboard

    def create_markup(self):
        return InlineKeyboardMarkup(self.keyboard)



