import logging
import logging.handlers
import configparser
import datetime
import sqlite3

PURGE_DAYS = 180

config = configparser.ConfigParser()
config.read('cortexpal.ini')

logHandler = logging.handlers.TimedRotatingFileHandler(filename=config['logging']['file'], when='D', backupCount=9)
logging.basicConfig(handlers=[logHandler], format='%(asctime)s %(message)s', level=logging.INFO)

db = sqlite3.connect(config['database']['file'])
db.row_factory = sqlite3.Row
cursor = db.cursor()

logging.info('Running the purge')
purge_time = datetime.now(timezone.utc) - timedelta(days=PURGE_DAYS)
games_to_purge = []
cursor.execute('SELECT * FROM GAME WHERE ACTIVITY<:purge_time', {'purge_time':purge_time})
fetching = True
while fetching:
    row = cursor.fetchone()
    if row:
        games_to_purge.append(row['GUID'])
    else:
        fetching = False
for game_guid in games_to_purge:
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

