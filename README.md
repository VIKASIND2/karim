# Karim
This Telegram Bot can connect to the Telegram Client with the user's credentials in order to access the client's functionalities. The bot can forward a select message to all the chat members in a selection of group chats or channels.

## Bot Commands
Currently, the bot will be able to respond to the following commands:
- ```/account``` -> Returns the current connection status to the Telegram Client (if the user is logged in and with which Telegram Account)
- ```/signin``` -> Asks the user to input Telegram Credentials and attempts to sign in the Telegram Client. No credentials will be stored in the server.
    * ```phone``` -> The user's telegram account's phone number (```+49 123 123 1234```)
    * ```code``` -> The security code sent by Telegram to verify the identity. It is important to send the code separated by dots (```1.2.3.4.5```) otherwise it will immediatelly expire.
    * ```password``` -> In case the user has set a 2-steps-verification password, this will be required to sign in correctly.
- ```/signout``` -> Signs out of the Telegram Client and deletes the session.
- ```/forward``` -> Allows the user to forward a message to all the chat members present in a selection of group chats, via the user's own account.