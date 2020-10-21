class Callbacks:
    """Object to store PTB conversations Callbacks"""
    CANCEL = 'CANCEL'
    NONE = 'NONE'
    DONE= 'DONE'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    LOGOUT = 'LOGOUT'
    LOGIN = 'LOGIN'
    SELECT = 'SELECT'
    UNSELECT = 'UNSELECT'
    CONFIRM = 'CONFIRM'
    REQUEST_CODE = 'REQUEST_CODE'
    NEWSLETTER = 'NEWSLETTER'
    INSTAGRAM_DM = 'INSTAGRAM_DM'
    TELEGRAM = 'TELEGRAM_GROUPS'


class LogInStates:
    """Object to store PTB Start Conversation Handler states indicators"""
    INPUT_PHONE = 1
    INPUT_PASSWORD = 2
    INPUT_CODE = 3


class LogOutStates:
    """Object to store PTB Sign Out Conversation Handler states indicators"""
    CONFIRM = 1


class ForwarderStates:
    """Object to store PTB Message Conversation Handler states indicators"""
    MODE = 1
    MESSAGE = 2
    SELECT_GROUP = 3
    CONFIRM = 4


class UnsubscribeStates:
    """Object to store PTB Unsubscribe Conversation Handler states indicators"""
    CONFIRM = 1


class Objects:
    PERSISTENCE = 1
    SESSION_MANAGER = 2
    FORWARDER = 3