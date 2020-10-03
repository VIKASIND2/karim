from typing import Dict

from rsa import key
from karim.bot.commands import *

class CreateMarkup():
    """
    Class describing a Reply Markup Menu.
    """
    def __init__(self, items: Dict, cols=1):
        self.items = items
        self.titles = items.values()
        self.callbacks = items.keys()
        self.cols = cols
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
        CreateMarkup.__init__(self, {title: Callbacks.NONE}, cols=1)


class ForwarderMarkup(CreateMarkup):
    def __init__(self, forwarder: Forwarder):
        self.selected_div = 'Selected Groups:'
        self.selected = forwarder.get_selection()
        self.shown_div = 'Select below:'
        self.shown_selection = forwarder.get_shown()
        self.arrows = {Callbacks.LEFT: '<-', Callbacks.RIGHT: '->'}
        self.options = {Callbacks.CANCEL: 'Cancel', Callbacks.DONE: 'Done'}
        self.set_keyboard()

    def set_keyboard(self):
        selected_div_kb = MarkupDivider(self.selected_div).create_keyboard()
        selected_kb = CreateMarkup(self.selected, cols=2).create_keyboard()
        shown_div_kb = MarkupDivider(self.shown_div).create_keyboard()
        shown_selection_kb = CreateMarkup(self.shown_selection).create_keyboard()
        arrows_kb = CreateMarkup(self.arrows, cols=2).create_keyboard()
        options_kb = CreateMarkup(self.options).create_keyboard()

        keyboard = [selected_div_kb]
        for row in selected_kb:
            keyboard.append(row)
        keyboard.append(shown_div_kb[0])
        for row in shown_selection_kb:
            keyboard.append(row)
        keyboard.append(arrows_kb[0])
        keyboard.append(options_kb[0])
        self.keyboard = keyboard
        return keyboard



