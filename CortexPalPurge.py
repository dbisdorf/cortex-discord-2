import CortexPal
import requests
import json
import configparser
import logging
import logging.handlers
import sqlite3
from datetime import datetime, timedelta, timezone

config = configparser.ConfigParser()
config.read('cortexpal.ini')

auth_request_headers = {
    "Authorization": "Bot {}".format(config['discord']['token'])
}

purge_days = int(config['purge']['days'])

logHandler = logging.handlers.TimedRotatingFileHandler(filename=config['logging']['file'], when='D', backupCount=9)
logging.basicConfig(handlers=[logHandler], format='%(asctime)s %(message)s', level=logging.DEBUG)

db = sqlite3.connect(config['database']['file'])
db.row_factory = sqlite3.Row
cursor = db.cursor()

logging.info('Running the purge')
purge_time = datetime.now(timezone.utc) - timedelta(days=purge_days)
games_to_purge = []
cursor.execute('SELECT * FROM GAME WHERE ACTIVITY<:purge_time', {'purge_time':purge_time})
fetching = True
while fetching:
    row = cursor.fetchone()
    if row:
        # give warning message
        game = CortexPal.CortexGame(db, row['SERVER'], row['CHANNEL'])
        if not game.is_empty():
            games_to_purge.append(row['GUID'])
            output = "**ATTENTION:**\nBecause you haven't used CortexPal2000 in this channel for {} days, the bot is now discarding the game data in this channel. Here's what your game looked like:\n\n".format(purge_days)
            output += game.output()
            message_json = {
                "content": output
            }
            r = requests.post(CortexPal.MESSAGE_URL.format(row['CHANNEL']), headers=auth_request_headers, json=message_json)
            message_response = json.loads(r.text)
            logging.debug(message_response)
    else:
        fetching = False
for game_guid in games_to_purge:
    logging.debug('Deleting game %s', game_guid)

    # delete from DB
    cursor.execute('DELETE FROM GAME_OPTIONS WHERE PARENT_GUID=:guid', {'guid':game_guid})
    cursor.execute('SELECT * FROM DICE_COLLECTION WHERE PARENT_GUID=:guid', {'guid':game_guid})
    collections = []
    fetching = True
    while fetching:
        row = cursor.fetchone()
        if row:
            collections.append(row['GUID'])
        else:
            fetching = False
    for collection_guid in collections:
        cursor.execute('DELETE FROM DIE WHERE PARENT_GUID=:guid', {'guid':collection_guid})
    cursor.execute('DELETE FROM DIE WHERE PARENT_GUID=:guid', {'guid':game_guid})
    cursor.execute('DELETE FROM DICE_COLLECTION WHERE PARENT_GUID=:guid', {'guid':game_guid})
    cursor.execute('DELETE FROM RESOURCE WHERE PARENT_GUID=:guid', {'guid':game_guid})
    cursor.execute('DELETE FROM GAME WHERE GUID=:guid', {'guid':game_guid})
    db.commit()

logging.info('Deleted %d games', len(games_to_purge))

cursor.execute('SELECT COUNT() FROM TALLY WHERE TALLY_DATE<:purge_time', {'purge_time':purge_time})
logging.info('Deleting %d tallies', cursor.fetchone()[0])

cursor.execute('DELETE FROM TALLY WHERE TALLY_DATE<:purge_time', {'purge_time':purge_time})
db.commit()

