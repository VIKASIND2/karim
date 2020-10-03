class Callbacks:
    """Object to store PTB conversations Callbacks"""
    CANCEL = 'CANCEL'


class StartStates:
    """Object to store PTB Start Conversation Handler states indicators"""
    INPUT_PHONE = 1
    INPUT_PASSWORD = 2
    INPUT_CODE = 3


class MessageStates:
    """Object to store PTB Message Conversation Handler states indicators"""
    SELECT_GROUP = 1
    SELECT_MESSAGE = 2