from karim.classes.callbacks import Objects
from karim.classes.forwarder import Forwarder
from karim.classes.session_manager import SessionManager
from karim.classes.persistence import Persistence

def dict_to_obj(obj_dict, method):
    print('CONVERTING DICT TO OBJ: ', obj_dict)
    if method == Objects.FORWARDER:
        obj = Forwarder(
                    method=obj_dict.get('method'), 
                    chat_id=obj_dict.get('chat_id'),
                    user_id=obj_dict.get('user_id'),
                    message_id=obj_dict.get('message_id'),
                    phone=obj_dict.get('phone'),
                    password=obj_dict.get('password'),
                    code=obj_dict.get('code'),
                    phone_code_hash=obj_dict.get('phone_code_hash'),
                    code_tries=obj_dict.get('code_tries'),
                    selected_ids=obj_dict.get('selected_ids'),
                    group_ids=obj_dict.get('group_ids'),
                    group_titles=obj_dict.get('group_titles'),
                    shown_ids=obj_dict.get('shown_ids'),
                    text=obj_dict.get('text'),
                    targets=obj_dict.get('targets'),
                    rotate_size=obj_dict.get('rotate_size'),
                    first_index=obj_dict.get('first_index'),
                    last_index=obj_dict.get('last_index'),
                    page_index=obj_dict.get('page_index'),
                    pages=obj_dict.get('pages')
                )
    elif method == Objects.SESSION_MANAGER:
        # Class is Session Manager
        obj = SessionManager(
            method=obj_dict.get('method'), 
            chat_id=obj_dict.get('chat_id'),
            user_id=obj_dict.get('user_id'),
            message_id=obj_dict.get('message_id'),
            phone=obj_dict.get('phone'),
            password=obj_dict.get('password'),
            code=obj_dict.get('code'),
            phone_code_hash=obj_dict.get('phone_code_hash'),
            code_tries=obj_dict.get('code_tries'),
        )
    else:
        obj = Persistence(
                method=obj_dict.get('method'), 
                chat_id=obj_dict.get('chat_id'),
                user_id=obj_dict.get('user_id'),
                message_id=obj_dict.get('message_id'),
            )
    return obj