# Help Command
help_text = '<b>Available Commands:</b>\n/account - Returns the current connection status to the Telegram Client (if the user is logged in and with which Telegram Account)\n\n/signin - Asks the user to input Telegram Credentials and attempts to sign in the Telegram Client. No credentials will be stored in the server.\n -> <code>phone</code> - The user\'s telegram account\'s phone number (<code>+49 123 123 1234</code>)\n -> <code>code</code> - The security code sent by Telegram to verify the identity. It is important to send the code separated by dots (<code>1.2.3.4.5</code>) otherwise it will immediatelly expire.\n -> <code>password</code> - In case the user has set a 2-steps-verification password, this will be required to sign in correctly.\n\n/signout - Signs out of the Telegram Client and deletes the session.\n\n/forward - Allows the user to forward a message to all the chat members present in a selection of group chats, via the user\'s own account.'

# START/SIGN IN CONVERSATION
client_already_signed_in = 'You are already signed into the Telegram Client. If you wish to sign in with another account, please make sure to log out first with /signout'
request_login_text = 'You will be asked your Telegram credentials, which will be used by the bot to log into the Telegram Client. No personal information will be saved.'
request_phone_text = 'Please enter below your Telegram phone number'
phone_not_valid = 'The phone number you entered is not valid. Make sure to send a valid phone number in the format: \n<code>+49 123 123 1234</code>'
request_code_text = 'You should now have received a security code from Telegram. Enter it below <i>making sure you insert dots (\'.\') between the digits of the code: <code>1.2.3.4.5</code> - otherwise the code will expire</i>'
client_signing_successful = 'You were able to sign into the Telegram Client successfully! You are now able to use this bot\'s features and commands. Type /help for a list of available commands.'
# SendCodeRequest Errors
request_password_text = 'Please enter below your Telegram password'
floodwaiterror_text = 'The security code was sent too many times. Try entering the last code you received.'
requestcodefailed_text = 'There was an error when requesting the security code. Please try again later.'
invalid_security_code = 'Invalid Security Code. Try again with the latest security code sent by Telegram. Make sure to include dots between the characters: <code>1.2.3.4.5</code>'
code_expired = 'The security code you entered has expired! Please enter the newly sent code in the following format: <code>1.2.3.4.5</code>'
# Signin Errors
failed_client_signin = 'There was an error when trying to sign into the Telegram Client. Try again or contact @davidwickerhf for support'
wrong_password_text = 'The provided password is incorrect. Please make sure to enter your Telegram password correctly below to complete the sign in procedure.'

# SIGN OUT COMMAND
confirm_sign_out_text = 'Are you sure you want to sign out of the Telegram Client? The bot won\'t be able to function correctly until you\'re signed in again'
sign_out_successful = 'You successfully signed out of the Telegram Client! To sign back in use /signin'
sign_out_unsuccessful = 'There was a problem in signing out of the Telegram Client... Try again or contact @davidwickerhf for support'
not_signed_in = 'You are not signed in yet! To sign in, use /signin'
sign_out_cancelled = 'Sign Out Cancelled. You are still signed into the client.'

# FORWARD MESSAGE CONVERSATION
client_not_connected = 'The client is not currently connected. Please sign into the Telegram Client with /signin'
failed_scrape_dialogues = 'There was a problem in retrieving the group chats from the Telegram API... Try again or contact @davidwickerhf for support'
send_message_to_forward = 'Send below the message you would like to forward:'
select_group_text = 'Select below the groups you wish to forward your message to. The bot will then forward your messages to all the users in such group'
confirm_forwarding = '<b>Are you sure you want to send the message above to all the chat members of the following groups?</b> {}'
cancel_forward_text = 'Forwarding Operation Cancelled. Your message has not been sent to any group.'

# ACCOUNT INFO COMMAND
account_info = '<b>Account Info</b>\nYou are currently signed into the Telegram Client with the account @{} (+{})'
no_connection = '<b>Client Connection</b>\nYou are currently not signed in with any account. The bot is currently not able to access the Telegram Client. To sign in, use /signin'
problem_connecting = 'There was a problem in connecting to the client... Try again.'
forward_successful = 'Forward successful! Your messages was sent successfully to {} users!'

# MULTIPLE UTILITIES
error_checking_connection = 'There was a problem in authenticating the client. Please try again or contact @davidwickerhf.'