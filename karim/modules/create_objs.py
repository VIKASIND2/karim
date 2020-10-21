from karim.classes.persistence import Persistence
from karim.classes.callbacks import Objects
from karim.classes.forwarder import Forwarder
from karim.classes.session_manager import SessionManager
from karim.classes.persistence import Persistence

def dict_to_obj(obj_dict, method):
    if method == Objects.FORWARDER:
        obj = Forwarder(
                    method=None if obj_dict.get('method') == -1 else obj_dict.get('method'), 
                    chat_id=None if obj_dict.get('chat_id') == -1 else obj_dict.get('chat_id'),
                    user_id=None if obj_dict.get('user_id') == -1 else obj_dict.get('user_id'),
                    message_id=None if obj_dict.get('message_id') == -1 else obj_dict.get('message_id'),
                    phone=None if obj_dict.get('phone') == -1 else obj_dict.get('phone'),
                    password=None if obj_dict.get('password') == -1 else obj_dict.get('password'),
                    code=None if obj_dict.get('code') == -1 else obj_dict.get('code'),
                    phone_code_hash=None if obj_dict.get('phone_code_hash') == -1 else obj_dict.get('phone_code_hash'),
                    code_tries=None if obj_dict.get('code_tries') == -1 else obj_dict.get('code_tries'),
                    mode=None if obj_dict.get('mode') == -1 else obj_dict.get('mode'),
                    selected_ids=None if obj_dict.get('selected_ids') == -1 else obj_dict.get('selected_ids'),
                    group_ids=None if obj_dict.get('group_ids') == -1 else obj_dict.get('group_ids'),
                    group_titles=None if obj_dict.get('group_titles') == -1 else obj_dict.get('group_titles'),
                    shown_ids=None if obj_dict.get('shown_ids') == -1 else obj_dict.get('shown_ids'),
                    text=None if obj_dict.get('text') == -1 else obj_dict.get('text'),
                    rotate_size=obj_dict.get('rotate_size'),
                    first_index=obj_dict.get('first_index'),
                    last_index=obj_dict.get('last_index'),
                    page_index=obj_dict.get('page_index'),
                    pages=None if obj_dict.get('pages') == -1 else obj_dict.get('pages'),
                    telethon_text=None if obj_dict.get('telethon_text') == -1 else obj_dict.get('telethon_text'),
                )
    elif method == Objects.SESSION_MANAGER:
        # Class == Session Manager
        obj = SessionManager(
            method=None if obj_dict.get('method') == -1 else obj_dict.get('method'), 
            chat_id=None if obj_dict.get('chat_id') == -1 else obj_dict.get('chat_id'),
            user_id=None if obj_dict.get('user_id') == -1 else obj_dict.get('user_id'),
            message_id=None if obj_dict.get('message_id') == -1 else obj_dict.get('message_id'),
            phone=None if obj_dict.get('phone') == -1 else obj_dict.get('phone'),
            password=None if obj_dict.get('password') == -1 else obj_dict.get('password'),
            code=None if obj_dict.get('code') == -1 else obj_dict.get('code'),
            phone_code_hash=None if obj_dict.get('phone_code_hash') == -1 else obj_dict.get('phone_code_hash'),
            code_tries=None if obj_dict.get('code_tries') == -1 else obj_dict.get('code_tries'),
        )
    else:
        obj = Persistence(
                method=None if obj_dict.get('method') == -1 else obj_dict.get('method'), 
                chat_id=None if obj_dict.get('chat_id') == -1 else obj_dict.get('chat_id'),
                user_id=None if obj_dict.get('user_id') == -1 else obj_dict.get('user_id'),
                message_id=None if obj_dict.get('message_id') == -1 else obj_dict.get('message_id'),
            )
    return obj