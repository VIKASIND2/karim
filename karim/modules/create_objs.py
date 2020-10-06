from karim.classes.callbacks import Objects
from karim.classes.forwarder import Forwarder
from karim.classes.session_manager import SessionManager
from karim.classes.persistence import Persistence

def dict_to_obj(obj_dict, method):
    print('CONVERTING DICT TO OBJ: ', obj_dict)
    if method == Objects.FORWARDER:
        obj = Forwarder(
                    method=None if obj_dict.get('method') is -1 else obj_dict.get('method'), 
                    chat_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    user_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    message_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    phone=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    password=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    code=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    phone_code_hash=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    code_tries=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    selected_ids=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    group_ids=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    group_titles=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    shown_ids=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    text=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    targets=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    rotate_size=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    first_index=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    last_index=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    page_index=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                    pages=None if obj_dict.get('method') is -1 else obj_dict.get('method')
                )
    elif method == Objects.SESSION_MANAGER:
        # Class is Session Manager
        obj = SessionManager(
            method=None if obj_dict.get('method') is -1 else obj_dict.get('method'), 
            chat_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            user_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            message_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            phone=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            password=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            code=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            phone_code_hash=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            code_tries=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
        )
    else:
        obj = Persistence(
                method=None if obj_dict.get('method') is -1 else obj_dict.get('method'), 
                chat_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                user_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
                message_id=None if obj_dict.get('method') is -1 else obj_dict.get('method'),
            )
    return obj