from karim.bot.commands import *

def sign_out(update, context):
    manager = SessionManager(update)
    if manager.check_connection():
        # User is logged in
        if manager.sign_out():
            # Log Out Successful
            update.effective_chat.send_message(sign_out_successful, parse_mode=ParseMode.HTML)
        else:
            # Error in Log Out 
            update.effective_chat.send_message(sign_out_unsuccessful, parse_mode=ParseMode.HTML)
    else:
        # User is not logged in
        update.effective_chat.send_message(not_signed_in, parse_mode=ParseMode.HTML)
        
