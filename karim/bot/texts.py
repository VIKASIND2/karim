import emoji
class symbols:
    CHECK = '✅' #emoji.emojize(':white_check_mark:')
    X = '❌' #emoji.emojize(':x:')
    PIN = emoji.emojize(':pushpin:')
    SEARCH = '🔎' #emoji.emojize(':mag_right:')

# Auth
not_authorized_text = 'You are not authorized to use this bot\'s features'

# Help Command
help_text = '<b>Available Commands:</b>\n/start - Use this command to subscribe to the newsletter.\n\n/unsubscribe - Use this command to unsubscribe from the newsletter and to stop receiving our messages.\n\n/adminhelp - Use this command to get a list of available commands if you are admin of this newsletter.'
not_admin_text = 'Sorry, this command can only be used by an admin.'
admin_help_text = '<b>Available Commands:</b>\n/account - Returns the current connection status to the Telegram Client (if the user is logged in and with which Telegram Account)\n\n/signin - Asks the user to input Telegram Credentials and attempts to sign in the Telegram Client. No credentials will be stored in the server.\n -> <code>phone</code> - The user\'s telegram account\'s phone number (<code>+49 123 123 1234</code>)\n -> <code>code</code> - The security code sent by Telegram to verify the identity. It is important to send the code separated by dots (<code>1.2.3.4.5</code>) otherwise it will immediatelly expire.\n -> <code>password</code> - In case the user has set a 2-steps-verification password, this will be required to sign in correctly.\n\n/signout - Signs out of the Telegram Client and deletes the session.\n\n/scrape - Allows you to scrape an instagram user\'s followers to use in the /forward command later.\n\n/forward - Allows the user to forward a message to all the chat members present in a selection of group chats, via the user\'s own account.'

# START NEWSLETTER COMMAND
checking_subscription = 'Checking subscription...'
already_subscribed_text = 'You are already subscribed to this newsletter! Thank you for taking interest in our content!'
subscription_successful_text = 'Thank you for subscribing to our newsletter! If you ever want to stop receiving our news, send /unsubscribe'
error_in_subscribing_text = 'Unfortunately there was an error when activating your subscription... Try again in some time...'

# UNSUBSCRIBE CONVERSATION
admin_cannot_unsubscribe = 'You cannot unsubscribe from the newsletter as you are the admin.'
confirm_unsubscription_text = 'Are you sure you want to unsubscribe from this newsletter?'
not_subscribed_yet_text = 'You are not subscribed to this newsletter yet! To activate your subscribption, simply type /start'
unsubscription_successful_text = 'You successfully unsubscribed from this newsletter. We are sorry to see you go! You ever want to subscribe again, justr type /start !'
unsubscription_cancelled_text = 'Your subscribtion is still active!'


# START/SIGN IN CONVERSATION
client_already_signed_in = 'You are already signed into the Telegram Client. If you wish to sign in with another account, please make sure to log out first with /signout'
request_login_text = 'You will be asked your Telegram credentials, which will be used by the bot to log into the Telegram Client. No personal information will be saved.'
request_phone_text = 'Please enter below your Telegram phone number'
phone_not_valid = 'The phone number you entered is not valid. Make sure to send a valid phone number in the format: \n<code>+49 123 123 1234</code>'
request_code_text = 'You should now have received a security code from Telegram. Enter it below <i>making sure you insert dots (\'.\') between the digits of the code: <code>1.2.3.4.5</code> - otherwise the code will expire</i>'
resend_code_text = 'The code has been sent again via SMS to your phone number. Please check your incoming SMSs. You might receive a call from Telegram which will dictate the security code to you. Please input such code below in the following format: <code>1.2.3.4.5</code>'
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

# SCRAPE CONVERSATION
input_username_text = 'Input below the instagram username you would like to get the followers for:'
user_not_valid_text = 'The user \'{}\' is not valid. Please try again below:'
user_private_text = 'The user \'{}\' is a private account, hence it\'s not possible to get it\'s followers. Please try again with another username:'
select_name_text = 'Input below a name for this follower\'s selection (can be customized, so that you can find it later)'
select_count_text = 'Select below the amount of followers you would like to scrape. Note that the higher the number, the longer the operation will take to complete.'
update_scraping_ig_text = 'Starting to scrape {} followers... This might take a while...'
cancelling_scrape_text = 'Scraping operation has been cancelled.'
# Instagram Scrape Job
failed_scraping_ig_text = 'There was an error when scraping the followers. Please try again in a bit or contact a developer of the bot'
update_scrape_status_text = 'A batch of followers has been scraped... Continuing scrape operation...'
finished_scrape_text = 'The scrape operation has been completed successfully! {} followers have been scraped and saved into the Google Sheet below:'

# FORWARD MESSAGE CONVERSATION
client_not_connected = 'The client is not currently connected. Please sign into the Telegram Client with /signin'
select_forward_mode_text = 'Select below on which platform you would like to forward your message:'
# Newsletter
confirm_send_newsletter_text = 'Are you sure you want to send your message through the Karim newsletter to {} users?'
inform_sending_newsletter_text = 'You message is being sent to your newsletter...'
# Instagram
no_selection_available_text = 'No IG users have been scraped so far. Please use /scrape to get a user\'s instagram followers.'
confirm_send_dm_text = 'Are you sure you want to send your message to {} instagram users?'
inform_sending_dms_text = 'You message is being sent to the selected instagram followers... This might take a while...'
finished_sending_dm_text = 'You message has been successfully sent to the users. {} failed.'
# Telegram
failed_scrape_dialogues = 'There was a problem in retrieving the group chats from the Telegram API... Try again or contact @davidwickerhf for support'
send_message_to_forward = 'Send below the message you would like to forward:'
select_group_text = 'Select below the groups you wish to forward your message to. The bot will then forward your messages to all the users in such group'
confirm_forwarding = '<b>Are you sure you want to send the message above to all the chat members of the following groups?</b> {}'
cancel_forward_text = 'Forwarding Operation Cancelled. Your message has not been sent to any group.'
preparing_queue_text = 'Preparing to send messages... Operation might take some time...'
sending_messages_text = 'Sending Messages to {} Users... {} sent so far...'
message_queue_finished = 'Message forwarding operation finished!'
flood_limit_reached = 'Too many messages were sent at once... Forwarding Operation cancelled. Message was sent to {} users. Check to see if your account has been limited by Telegram with @SpamBot'
error_sending_messages = 'There was an error while sending the messages... So far, the message has been sent to {} users.'

# ACCOUNT INFO COMMAND
account_info = '<b>Account Info</b>\nYou are currently signed into the Telegram Client with the account @{} (+{})'
no_connection = '<b>Client Connection</b>\nYou are currently not signed in with any account. The bot is currently not able to access the Telegram Client. To sign in, use /signin'
problem_connecting = 'There was a problem in connecting to the client... Try again.'
forward_successful = 'Forward successful! Your messages was sent successfully to {} users!'

# MULTIPLE UTILITIES
error_checking_connection = 'There was a problem in authenticating the client. Please try again or contact @davidwickerhf.'