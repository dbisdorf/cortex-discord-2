import configparser
import sqlite3

config = configparser.ConfigParser()
config.read('cortexpal.ini')

db = sqlite3.connect(config['database']['file'])
db.row_factory = sqlite3.Row
cursor = db.cursor()

cursor.execute(
'CREATE TABLE IF NOT EXISTS GAME'
'(GUID VARCHAR(32) PRIMARY KEY,'
'SERVER INT NOT NULL,'
'CHANNEL INT NOT NULL,'
'ACTIVITY DATETIME NOT NULL)'
)

cursor.execute(
'CREATE TABLE IF NOT EXISTS GAME_OPTIONS'
'(GUID VARCHAR(32) PRIMARY KEY,'
'KEY VARCHAR(16) NOT NULL,'
'VALUE VARCHAR(256),'
'PARENT_GUID VARCHAR(32) NOT NULL)'
)

cursor.execute(
'CREATE TABLE IF NOT EXISTS DIE'
'(GUID VARCHAR(32) PRIMARY KEY,'
'NAME VARCHAR(64),'
'SIZE INT NOT NULL,'
'QTY INT NOT NULL,'
'PARENT_GUID VARCHAR(32) NOT NULL)'
)

cursor.execute(
'CREATE TABLE IF NOT EXISTS DICE_COLLECTION'
'(GUID VARCHAR(32) PRIMARY KEY,'
'CATEGORY VARCHAR(64) NOT NULL,'
'GRP VARCHAR(64),'
'PARENT_GUID VARCHAR(32) NOT NULL)'
)

cursor.execute(
'CREATE TABLE IF NOT EXISTS RESOURCE'
'(GUID VARCHAR(32) PRIMARY KEY,'
'CATEGORY VARCHAR(64) NOT NULL,'
'NAME VARCHAR(64) NOT NULL,'
'QTY INT NOT NULL,'
'PARENT_GUID VARCHAR(64) NOT NULL)'
)

