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


class StartStates:
    """Object to store PTB Start Conversation Handler states indicators"""
    INPUT_PHONE = 1
    INPUT_PASSWORD = 2
    INPUT_CODE = 3


class LogOutStates:
    """Object to store PTB Sign Out Conversation Handler states indicators"""
    CONFIRM = 1


class MessageStates:
    """Object to store PTB Message Conversation Handler states indicators"""
    MESSAGE = 1
    SELECT_GROUP = 2
    CONFIRM = 3

class Objects:
    PERSISTENCE = 1
    SESSION_MANAGER = 2
    FORWARDER = 3