# cortex-discord-2
CortexPal2000 is a Discord bot to support playing the Cortex Prime RPG, using Discord slash commands.

## Contact the Developer
My Discord handle is Don#2462, and my Twitter handle is @dbisdorf. Feel free to contact me with any bug reports, or, if you prefer, you can file them on GitHub.

## Inviting the Bot
I have a public instance of this bot running 24/7. I can't guarantee it will be up 100% of the time; bugs or other issues may cause the bot to go down unexpectedly and to stay down for an indeterminate duration. You can invite this bot to your Discord server by giving this URL to your browser: https://discord.com/api/oauth2/authorize?client_id=697790419035226112&permissions=10240&scope=bot%20applications.commands

## Usage
This bot uses Discord's slash commands feature. You communicate with the bot by executing commands like this:

```
/pool roll name:doom
```

The elements of a command are:

* A forward slash
* The name of the command (like "pool")
* If necessary, the name of a subcommand (like "roll")
* Any necessary options (like "name:doom")

Discord will provide interactive suggestions as you type and will autocomplete some words for you.

Run the "/help" command to get a list of all CortexPal2000's commands. You can also get help for a specific command by running, for example, "/help command:pool" or "/help command:roll".

## Abandoned Games
If no one updates any game information in a given channel for a while, the bot will delete all game information in that channel. The clean-up time period is configurable.

## Dependencies

Aside from several standard Python libraries, CortexPal2000 also depends on:

* endpoints (https://pypi.org/project/endpoints/)
* discord_interactions (https://pypi.org/project/discord-py-interactions/)

## Hosting
If you're hosting your own instance of CortexPal2000, do the following:

* Your first step should be to register an application through the Discord Developer Portal. Make note of your application's new public key and bot token.
* Before running any of the scripts, configure all the options in cortexpal.ini. It should look something like this:

```
[logging]
file=(path and filename for the application log file)

[discord]
token=(the Discord bot token, from the developer portal)
public_key=(the Discord application public key, from the developer portal)

[database]
file=(the path and filename for the database file)

[purge]
days=(the number of days to wait before deleting game information in an inactive channel)
```

* Run CortexPalDatabase.py to initialize the sqlite database.
* Run CortexPalRegister.py to register all of the bot's commands with Discord.
* Set up a virtual environment (https://docs.python.org/3/library/venv.html) within which the bot will execute.
* Configure your web server to invoke the bot's wsgi.py script, within the virtual environment, as a WSGI application. For instance, if you're using Apache and mod_wsgi, you'd add something like this to your Apache configuration:

```
WSGIScriptAlias /cortex-pal /path/to/cortex-discord-2/wsgi.py process-group=cortex-pal
WSGIDaemonProcess cortex-pal python-home=/path/to/cortex-discord-2/venv home=/path/to/cortex-discord-2
WSGIProcessGroup cortex-pal
```

* In the Discord Developer Portal, configure the "Interactions Endpoint URL" so that it points to the URL you configured in your web server. Discord will immediately validate this URL, so be sure the bot is available through your web server before you do this.
* Use cron or some other scheduling system to execute CortexPalPurge.py regularly.
* When you create invite links through the Discord Developer Portal, choose the "bot" and "application.commands" scopes, and the "send messages" and "manage messages" permissions.

## Donate
If CortexPal is useful for you, and you feel like buying me a cup of tea, you can reach me through PayPal:

https://paypal.me/DonaldBisdorf
