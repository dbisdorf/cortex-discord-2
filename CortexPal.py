# TODO
# What do we pass to command functions? DB? Cursor? Game object? Roller?

from endpoints import Controller, AccessDenied
from discord_interactions import verify_key, InteractionType, InteractionResponseType
import logging
import json
import configparser
import sqlite3
import random
import os
import traceback
import re
import uuid
from datetime import datetime, timedelta, timezone

PURGE_DAYS = 180

DICE_EXPRESSION = re.compile('(\d*(d|D))?(4|6|8|10|12)')
DIE_SIZES = [4, 6, 8, 10, 12]

UNTYPED_STRESS = 'General'

DIE_FACE_ERROR = '{0} is not a valid die size. You may only use dice with sizes of 4, 6, 8, 10, or 12.'
DIE_STRING_ERROR = '{0} is not a valid die or dice.'
DIE_EXCESS_ERROR = 'You can\'t use that many dice.'
DIE_MISSING_ERROR = 'There were no valid dice in that command.'
DIE_LACK_ERROR = 'That pool only has {0}D{1}.'
DIE_NONE_ERROR = 'That pool doesn\'t have any D{0}s.'
NOT_EXIST_ERROR = 'There\'s no such {0} yet.'
HAS_NONE_ERROR = '{0} doesn\'t have any {1}.'
HAS_ONLY_ERROR = '{0} only has {1} {2}.'
INSTRUCTION_ERROR = '`{0}` is not a valid instruction for the `{1}` command.'
UNKNOWN_COMMAND_ERROR = 'That\'s not a valid command.'
JOIN_ERROR = 'The #{0} channel does not allow other channels to join. Future commands apply only to this channel.'
UNEXPECTED_ERROR = 'Oops. A software error interrupted this command.'

BEST_OPTION = 'best'
JOIN_OPTION = 'join'

GAME_INFO_HEADER = '**Cortex Game Information**'
ABOUT_TEXT = 'CortexPal2000 v1.0.0: a Discord bot for Cortex Prime RPG players.'

# Read configuration.

config = configparser.ConfigParser()
config.read('cortexpal.ini')

# Set up logging.

logger = logging.getLogger(__name__)

# Classes and functions follow.

class DiscordResponse:
    elements = {}

    def __init__(self, text):
        self.elements['type'] = InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE
        self.elements['data'] = {'content': str(text)}

    def json(self):
        return self.elements

class DiscordResponsePong(DiscordResponse):
    def __init__(self):
        self.elements['type'] = InteractionResponseType.PONG

class CortexError(Exception):
    """Exception class for command and rules errors specific to this bot."""

    def __init__(self, message, *args):
        self.message = message
        self.args = args

    def __str__(self):
        return self.message.format(*(self.args))

def parse_string_into_dice(words):
    """Sort the words of an input string, and identify which are dice notations and which are not."""

    dice = []
    for word in words.split(' '):
        dice.append(Die(word))
    return dice

def capitalize_words(words):
    """Sort the words of an input string, and identify which are numerals and which are not."""

    capitalized = []
    for word in words:
        capitalized.append(word.lower().capitalize())
    return ' '.join(capitalized)

def fetch_all_dice_for_parent(db_parent):
    """Given an object from the database, get all the dice that belong to it."""

    dice = []
    db_parent.cursor.execute('SELECT * FROM DIE WHERE PARENT_GUID=:PARENT_GUID', {'PARENT_GUID':db_parent.db_guid})
    fetching = True
    while fetching:
        row = db_parent.cursor.fetchone()
        if row:
            die = Die(name=row['NAME'], size=row['SIZE'], qty=row['QTY'])
            die.already_in_db(db_parent.db, db_parent, row['GUID'])
            dice.append(die)
        else:
            fetching = False
    return dice

def purge():
    """Scan for old unused games and remove them."""

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

class Die:
    """A single die, or a set of dice of the same size."""

    def __init__(self, expression=None, name=None, size=4, qty=1):
        self.name = name
        self.size = size
        self.qty = qty
        self.db_parent = None
        self.db_guid = None
        self.db = None
        self.cursor = None
        if expression:
            if not DICE_EXPRESSION.fullmatch(expression):
                raise CortexError(DIE_STRING_ERROR, expression)
            numbers = expression.lower().split('d')
            if len(numbers) == 1:
                self.size = int(numbers[0])
            else:
                if numbers[0]:
                    self.qty = int(numbers[0])
                self.size = int(numbers[1])

    def store_in_db(self, db, db_parent):
        """Store this die in the database, under a given parent."""

        self.db = db
        self.cursor = self.db.cursor()
        self.db_parent = db_parent
        self.db_guid = uuid.uuid1().hex
        self.cursor.execute('INSERT INTO DIE (GUID, NAME, SIZE, QTY, PARENT_GUID) VALUES (?, ?, ?, ?, ?)', (self.db_guid, self.name, self.size, self.qty, self.db_parent.db_guid))
        self.db.commit()

    def already_in_db(self, db, db_parent, db_guid):
        """Inform the Die that it is already in the database, under a given parent and guid."""

        self.db = db
        self.cursor = self.db.cursor()
        self.db_parent = db_parent
        self.db_guid = db_guid

    def remove_from_db(self):
        """Remove this Die from the database."""

        if self.db_guid:
            self.cursor.execute('DELETE FROM DIE WHERE GUID=:guid', {'guid':self.db_guid})
            self.db.commit()

    def step_down(self):
        """Step down the die size."""

        if self.size > 4:
            self.update_size(self.size - 2)

    def step_up(self):
        """Step up the die size."""

        if self.size < 12:
            self.update_size(self.size + 2)

    def combine(self, other_die):
        """Combine this die with another die (as when applying a new stress die to existing stress)."""

        if self.size < other_die.size:
            self.update_size(other_die.size)
        elif self.size < 12:
            self.update_size(self.size + 2)

    def update_size(self, new_size):
        """Change the size of the die."""

        self.size = new_size
        if self.db_guid:
            self.cursor.execute('UPDATE DIE SET SIZE=:size WHERE GUID=:guid', {'size':self.size, 'guid':self.db_guid})
            self.db.commit()

    def update_qty(self, new_qty):
        """Change the quantity of the dice."""

        self.qty = new_qty
        if self.db_guid:
            self.cursor.execute('UPDATE DIE SET QTY=:qty WHERE GUID=:guid', {'qty':self.qty, 'guid':self.db_guid})

    def is_max(self):
        """Identify whether the Die is at the maximum allowed size."""

        return self.size == 12

    def output(self):
        """Return the Die as a string suitable for output in Discord."""

        return str(self)

    def __str__(self):
        """General purpose string representation of the Die."""

        if self.qty > 1:
            return '{0}D{1}'.format(self.qty, self.size)
        else:
            return 'D{0}'.format(self.size)

class NamedDice:
    """A collection of user-named single-die traits, suitable for complications and assets."""

    def __init__(self, db, category, group, db_parent, db_guid=None):
        self.db = db
        self.cursor = db.cursor()
        self.dice = {}
        self.category = category
        self.group = group
        self.db_parent = db_parent
        if db_guid:
            self.db_guid = db_guid
        else:
            if self.group:
                self.cursor.execute('SELECT * FROM DICE_COLLECTION WHERE PARENT_GUID=:PARENT_GUID AND CATEGORY=:category AND GRP=:group', {'PARENT_GUID':self.db_parent.db_guid, 'category':self.category, 'group':self.group})
            else:
                self.cursor.execute('SELECT * FROM DICE_COLLECTION WHERE PARENT_GUID=:PARENT_GUID AND CATEGORY=:category AND GRP IS NULL', {'PARENT_GUID':self.db_parent.db_guid, 'category':self.category})
            row = self.cursor.fetchone()
            if row:
                self.db_guid = row['GUID']
            else:
                self.db_guid = uuid.uuid1().hex
                self.cursor.execute('INSERT INTO DICE_COLLECTION (GUID, CATEGORY, GRP, PARENT_GUID) VALUES (?, ?, ?, ?)', (self.db_guid, self.category, self.group, self.db_parent.db_guid))
                self.db.commit()
        fetched_dice = fetch_all_dice_for_parent(self)
        for die in fetched_dice:
            self.dice[die.name] = die

    def remove_from_db(self):
        """Remove these NamedDice from the database."""

        for name in list(self.dice):
            self.dice[name].remove_from_db()
        self.cursor.execute("DELETE FROM DICE_COLLECTION WHERE GUID=:db_guid", {'db_guid':self.db_guid})
        self.db.commit()
        self.dice = {}

    def is_empty(self):
        """Identify whether there are any dice in this object."""

        return not self.dice

    def add(self, name, die):
        """Add a new die, with a given name."""

        die.name = name
        if not name in self.dice:
            die.store_in_db(self.db, self)
            self.dice[name] = die
            return 'New: ' + self.output(name)
        elif self.dice[name].is_max():
            return 'This would step up beyond {0}'.format(self.output(name))
        else:
            self.dice[name].combine(die)
            return 'Raised to ' + self.output(name)

    def remove(self, name):
        """Remove a die with a given name."""

        if not name in self.dice:
            raise CortexError(NOT_EXIST_ERROR, self.category)
        output = 'Removed: ' + self.output(name)
        self.dice[name].remove_from_db()
        del self.dice[name]
        return output

    def step_up(self, name):
        """Step up the die with a given name."""

        if not name in self.dice:
            raise CortexError(NOT_EXIST_ERROR, self.category)
        if self.dice[name].is_max():
            return 'This would step up beyond {0}'.format(self.output(name))
        self.dice[name].step_up()
        return 'Stepped up to ' + self.output(name)

    def step_down(self, name):
        """Step down the die with a given name."""

        if not name in self.dice:
            raise CortexError(NOT_EXIST_ERROR, self.category)
        if self.dice[name].size == 4:
            self.remove(name)
            return 'Stepped down and removed: ' + name
        else:
            self.dice[name].step_down()
            return 'Stepped down to ' + self.output(name)

    def get_all_names(self):
        """Identify the names of all the dice in this object."""

        return list(self.dice)

    def output(self, name):
        """For a die of a given name, return a formatted description of that die."""

        return '{0} {1}'.format(self.dice[name].output(), name)

    def output_all(self, separator='\n'):
        """Return a formatted description of all the dice in this object."""

        output = ''
        prefix = ''
        for name in list(self.dice):
            output += prefix + self.output(name)
            prefix = separator
        return output

class DicePool:
    """A single-purpose collection of die sizes and quantities, suitable for doom pools, crisis pools, and growth pools."""

    def __init__(self, db, group, incoming_dice=[]):
        self.db = db
        self.cursor = db.cursor()
        self.group = group
        self.dice = [None, None, None, None, None]
        self.db_parent = None
        self.db_guid = None
        if incoming_dice:
            self.add(incoming_dice)

    def store_in_db(self, db_parent):
        """Store this pool in the database."""

        self.db_guid = uuid.uuid1().hex
        self.db_parent = db_parent
        self.cursor.execute("INSERT INTO DICE_COLLECTION (GUID, CATEGORY, GRP, PARENT_GUID) VALUES (?, 'pool', ?, ?)", (self.db_guid, self.group, self.db_parent.db_guid))
        self.db.commit()

    def already_in_db(self, db_parent, db_guid):
        """Inform the pool that it is already in the database, under a given parent and guid."""

        self.db_parent = db_parent
        self.db_guid = db_guid

    def fetch_dice_from_db(self):
        """Get all the dice from the database that would belong to this pool."""

        fetched_dice = fetch_all_dice_for_parent(self)
        for die in fetched_dice:
            self.dice[DIE_SIZES.index(die.size)] = die

    def disconnect_from_db(self):
        """Prevent further changes to this pool from affecting the database."""

        self.db_parent = None
        self.db_guid = None

    def is_empty(self):
        """Identify whether this pool is empty."""

        return not self.dice

    def remove_from_db(self):
        """Remove this entire pool from the database."""

        for index in range(len(self.dice)):
            if self.dice[index]:
                self.dice[index].remove_from_db()
        self.cursor.execute("DELETE FROM DICE_COLLECTION WHERE GUID=:db_guid", {'db_guid':self.db_guid})
        self.db.commit()
        self.dice = [None, None, None, None, None]

    def add(self, dice):
        """Add dice to the pool."""

        for die in dice:
            index = DIE_SIZES.index(die.size)
            if self.dice[index]:
                self.dice[index].update_qty(self.dice[index].qty + die.qty)
            else:
                self.dice[index] = die
                if self.db_parent and not die.db_parent:
                    die.store_in_db(self.db, self)
        return self.output()

    def remove(self, dice):
        """Remove dice from the pool."""

        for die in dice:
            index = DIE_SIZES.index(die.size)
            if self.dice[index]:
                stored_die = self.dice[index]
                if die.qty > stored_die.qty:
                    raise CortexError(DIE_LACK_ERROR, stored_die.qty, stored_die.size)
                stored_die.update_qty(stored_die.qty - die.qty)
                if stored_die.qty == 0:
                    if self.db_parent:
                        stored_die.remove_from_db()
                    self.dice[index] = None
            else:
                raise CortexError(DIE_NONE_ERROR, die.size)
        return self.output()

    def temporary_copy(self):
        """Return a temporary, non-persisted copy of this dice pool."""
        copy = DicePool(self.group)
        dice_copies = []
        for die in self.dice:
            if die:
                dice_copies.append(Die(size=die.size, qty=die.qty))
        copy.add(dice_copies)
        return copy

    def roll(self, roller, suggest_best=False):
        """Roll all the dice in the pool, and return a formatted summary of the results."""

        output = ''
        separator = ''
        rolls = []
        for die in self.dice:
            if die:
                output += '{0}D{1} : '.format(separator, die.size)
                for num in range(die.qty):
                    roll = {'value': roller.roll(die.size), 'size': die.size}
                    roll_str = str(roll['value'])
                    if roll_str == '1':
                        roll_str = '**(1)**'
                    else:
                        rolls.append(roll)
                    output += roll_str + ' '
                separator = '\n'
        if suggest_best:
            if len(rolls) == 0:
                output += '\nBotch!'
            else:
                # Calculate best total, then choose an effect die
                rolls.sort(key=lambda roll: roll['value'], reverse=True)
                best_total_1 = rolls[0]['value']
                best_addition_1 = '{0}'.format(rolls[0]['value'])
                best_effect_1 = 'D4'
                if len(rolls) > 1:
                    best_total_1 += rolls[1]['value']
                    best_addition_1 = '{0} + {1}'.format(best_addition_1, rolls[1]['value'])
                    if len(rolls) > 2:
                        resorted_rolls = sorted(rolls[2:], key=lambda roll: roll['size'], reverse=True)
                        best_effect_1 = 'D{0}'.format(resorted_rolls[0]['size'])
                output += '\nBest Total: {0} ({1}) with Effect: {2}'.format(best_total_1, best_addition_1, best_effect_1)

                # Find best effect die, then chooose best total
                rolls.sort(key=lambda roll: roll['value'])
                rolls.sort(key=lambda roll: roll['size'], reverse=True)
                best_total_2 = rolls[0]['value']
                best_addition_2 = '{0}'.format(rolls[0]['value'])
                best_effect_2 = 'D4'
                if len(rolls) > 1:
                    best_total_2 += rolls[1]['value']
                    best_addition_2 = '{0} + {1}'.format(best_addition_2, rolls[1]['value'])
                    if len(rolls) > 2:
                        best_effect_2 = 'D{0}'.format(rolls[0]['size'])
                        resorted_rolls = sorted(rolls[1:], key=lambda roll: roll['value'], reverse=True)
                        best_total_2 = resorted_rolls[0]['value'] + resorted_rolls[1]['value']
                        best_addition_2 = '{0} + {1}'.format(resorted_rolls[0]['value'], resorted_rolls[1]['value'])
                if best_effect_1 != best_effect_1 or best_total_1 != best_total_2:
                    output += ' | Best Effect: {0} with Total: {1} ({2})'.format(best_effect_2, best_total_2, best_addition_2)
        return output

    def output(self):
        """Return a formatted list of the dice in this pool."""

        if self.is_empty():
            return 'empty'
        output = ''
        for die in self.dice:
            if die:
                output += die.output() + ' '
        return output

class DicePools:
    """A collection of DicePool objects."""

    def __init__(self, db, db_parent):
        self.db = db
        self.cursor = db.cursor()
        self.pools = {}
        self.db_parent = db_parent
        self.cursor.execute('SELECT * FROM DICE_COLLECTION WHERE CATEGORY="pool" AND PARENT_GUID=:PARENT_GUID', {'PARENT_GUID':self.db_parent.db_guid})
        pool_info = []
        fetching = True
        while fetching:
            row = self.cursor.fetchone()
            if row:
                pool_info.append({'db_guid':row['GUID'], 'grp':row['GRP'], 'parent_guid':row['PARENT_GUID']})
            else:
                fetching = False
        for fetched_pool in pool_info:
            new_pool = DicePool(fetched_pool['grp'])
            new_pool.already_in_db(fetched_pool['parent_guid'], fetched_pool['db_guid'])
            new_pool.fetch_dice_from_db()
            self.pools[new_pool.group] = new_pool

    def is_empty(self):
        """Identify whether we have any pools."""

        return not self.pools

    def remove_from_db(self):
        """Remove all of these pools from the database."""

        for group in list(self.pools):
            self.pools[group].remove_from_db()
        self.pools = {}

    def add(self, group, dice):
        """Add some dice to a pool under a given name."""

        if not group in self.pools:
            self.pools[group] = DicePool(group)
            self.pools[group].store_in_db(self.db_parent)
        self.pools[group].add(dice)
        return '{0}: {1}'.format(group, self.pools[group].output())

    def remove(self, group, dice):
        """Remove some dice from a pool with a given name."""

        if not group in self.pools:
            raise CortexError(NOT_EXIST_ERROR, 'pool')
        self.pools[group].remove(dice)
        return '{0}: {1}'.format(group, self.pools[group].output())

    def clear(self, group):
        """Remove one entire pool."""
        if not group in self.pools:
            raise CortexError(NOT_EXIST_ERROR, 'pool')
        self.pools[group].remove_from_db()
        del self.pools[group]
        return 'Cleared {0} pool.'.format(group)

    def temporary_copy(self, group):
        """Return an independent, non-persistent copy of a pool."""

        if not group in self.pools:
            raise CortexError(NOT_EXIST_ERROR, 'pool')
        return self.pools[group].temporary_copy()

    def roll(self, group, suggest_best=False):
        """Roll all the dice in a certain pool and return the results."""

        return self.pools[group].roll(suggest_best)

    def output(self):
        """Return a formatted summary of all the pools in this object."""

        output = ''
        prefix = ''
        for key in list(self.pools):
            output += '{0}{1}: {2}'.format(prefix, key, self.pools[key].output())
            prefix = '\n'
        return output

class Resources:
    """Holds simple quantity-based resources, like plot points."""

    def __init__(self, db, category, db_parent):
        self.db = db
        self.cursor = db.cursor()
        self.resources = {}
        self.category = category
        self.db_parent = db_parent
        self.cursor.execute("SELECT * FROM RESOURCE WHERE PARENT_GUID=:PARENT_GUID AND CATEGORY=:category", {'PARENT_GUID':self.db_parent.db_guid, 'category':self.category})
        fetching = True
        while fetching:
            row = self.cursor.fetchone()
            if row:
                self.resources[row['NAME']] = {'qty':row['QTY'], 'db_guid':row['GUID']}
            else:
                fetching = False

    def is_empty(self):
        """Identify whether there are any resources stored here."""

        return not self.resources

    def remove_from_db(self):
        """Removce these resources from the database."""

        self.cursor.executemany("DELETE FROM RESOURCE WHERE GUID=:db_guid", [{'db_guid':self.resources[resource]['db_guid']} for resource in list(self.resources)])
        self.db.commit()
        self.resources = {}

    def add(self, name, qty=1):
        """Add a quantity of resources to a given name."""

        if not name in self.resources:
            db_guid = uuid.uuid1().hex
            self.resources[name] = {'qty':qty, 'db_guid':db_guid}
            self.cursor.execute("INSERT INTO RESOURCE (GUID, CATEGORY, NAME, QTY, PARENT_GUID) VALUES (?, ?, ?, ?, ?)", (db_guid, self.category, name, qty, self.db_parent.db_guid))
            self.db.commit()
        else:
            self.resources[name]['qty'] += qty
            self.cursor.execute("UPDATE RESOURCE SET QTY=:qty WHERE GUID=:db_guid", {'qty':self.resources[name]['qty'], 'db_guid':self.resources[name]['db_guid']})
            self.db.commit()
        return self.output(name)

    def remove(self, name, qty=1):
        """Remove a quantity of resources from a given name."""

        if not name in self.resources:
            raise CortexError(HAS_NONE_ERROR, name, self.category)
        if self.resources[name]['qty'] < qty:
            raise CortexError(HAS_ONLY_ERROR, name, self.resources[name]['qty'], self.category)
        self.resources[name]['qty'] -= qty
        self.cursor.execute("UPDATE RESOURCE SET QTY=:qty WHERE GUID=:db_guid", {'qty':self.resources[name]['qty'], 'db_guid':self.resources[name]['db_guid']})
        self.db.commit()
        return self.output(name)

    def clear(self, name):
        """Remove a name from the catalog entirely."""
        if not name in self.resources:
            raise CortexError(HAS_NONE_ERROR, name, self.category)
        self.cursor.execute("DELETE FROM RESOURCE WHERE GUID=:db_guid", {'db_guid':self.resources[name]['db_guid']})
        self.db.commit()
        del self.resources[name]
        return 'Cleared {0} from {1} list.'.format(name, self.category)

    def output(self, name):
        """Return a formatted description of the resources held by a given name."""

        return '{0}: {1}'.format(name, self.resources[name]['qty'])

    def output_all(self):
        """Return a formatted summary of all resources."""

        output = ''
        prefix = ''
        for name in list(self.resources):
            output += prefix + self.output(name)
            prefix = '\n'
        return output

class GroupedNamedDice:
    """Holds named dice that are separated by groups, such as mental and physical stress (the dice names) assigned to characters (the dice groups)."""

    def __init__(self, db, category, db_parent):
        self.db = db
        self.cursor = db.cursor()
        self.groups = {}
        self.category = category
        self.db_parent = db_parent
        self.cursor.execute("SELECT * FROM DICE_COLLECTION WHERE PARENT_GUID=:parent_guid AND CATEGORY=:category", {'parent_guid':self.db_parent.db_guid, 'category':self.category})
        group_guids = {}
        fetching = True
        while fetching:
            row = self.cursor.fetchone()
            if row:
                group_guids[row['GRP']] = row['GUID']
            else:
                fetching = False
        for group in group_guids:
            new_group = NamedDice(self.category, group, self.db_parent, db_guid=group_guids[group])
            self.groups[group] = new_group

    def is_empty(self):
        """Identifies whether we're holding any dice yet."""

        return not self.groups

    def remove_from_db(self):
        """Remove all of these dice from the database."""

        for group in list(self.groups):
            self.groups[group].remove_from_db()
        self.groups = {}

    def add(self, group, name, die):
        """Add dice with a given name to a given group."""

        if not group in self.groups:
            self.groups[group] = NamedDice(self.category, group, self.db_parent)
        return self.groups[group].add(name, die)

    def remove(self, group, name):
        """Remove dice with a given name from a given group."""

        if not group in self.groups:
            raise CortexError(HAS_NONE_ERROR, group, self.category)
        return self.groups[group].remove(name)

    def clear(self, group):
        """Remove all dice from a given group."""

        if not group in self.groups:
            raise CortexError(HAS_NONE_ERROR, group, self.category)
        self.groups[group].remove_from_db()
        del self.groups[group]
        return 'Cleared all {0} for {1}.'.format(self.category, group)

    def step_up(self, group, name):
        """Step up the die with a given name, within a given group."""

        if not group in self.groups:
            raise CortexError(HAS_NONE_ERROR, group, self.category)
        return self.groups[group].step_up(name)

    def step_down(self, group, name):
        """Step down the die with a given name, within a given group."""

        if not group in self.groups:
            raise CortexError(HAS_NONE_ERROR, group, self.category)
        return self.groups[group].step_down(name)

    def output(self, group):
        """Return a formatted list of all the dice within a given group."""

        if self.groups[group].is_empty():
            return '{0}: None'.format(group)
        return '{0}: {1}'.format(group, self.groups[group].output_all(separator=', '))

    def output_all(self):
        """Return a formatted summary of all dice under all groups."""

        output = ''
        prefix = ''
        for group in list(self.groups):
            output += prefix + self.output(group)
            prefix = '\n'
        return output

class CortexGame:
    """All information for a game, within a single server and channel."""

    def __init__(self, db, server, channel):
        self.db = db
        self.cursor = db.cursor()
        self.server = server
        self.channel = channel
        self.pinned_message = None

        self.cursor.execute('SELECT * FROM GAME WHERE SERVER=:server AND CHANNEL=:channel', {"server":server, "channel":channel})
        row = self.cursor.fetchone()
        if not row:
            self.db_guid = uuid.uuid1().hex
            self.cursor.execute('INSERT INTO GAME (GUID, SERVER, CHANNEL, ACTIVITY) VALUES (?, ?, ?, ?)', (self.db_guid, server, channel, datetime.now(timezone.utc)))
            self.db.commit()
        else:
            self.db_guid = row['GUID']
        self.new()

    def new(self):
        """Set up new, empty traits for the game."""

        self.complications = NamedDice(self.db, 'complication', None, self)
        self.assets = NamedDice(self.db, 'asset', None, self)
        self.pools = DicePools(self.db, self)
        self.plot_points = Resources(self.db, 'plot points', self)
        self.stress = GroupedNamedDice(self.db, 'stress', self)
        self.xp = Resources(self.db, 'xp', self)

    def clean(self):
        """Resets and erases the game's traits."""

        self.complications.remove_from_db()
        self.assets.remove_from_db()
        self.pools.remove_from_db()
        self.plot_points.remove_from_db()
        self.stress.remove_from_db()
        self.xp.remove_from_db()

    def output(self):
        """Return a report of all of the game's traits."""

        output = GAME_INFO_HEADER + '\n'
        if not self.assets.is_empty():
            output += '\n**Assets**\n'
            output += self.assets.output_all()
            output += '\n'
        if not self.complications.is_empty():
            output += '\n**Complications**\n'
            output += self.complications.output_all()
            output += '\n'
        if not self.stress.is_empty():
            output += '\n**Stress**\n'
            output += self.stress.output_all()
            output += '\n'
        if not self.plot_points.is_empty():
            output += '\n**Plot Points**\n'
            output += self.plot_points.output_all()
            output += '\n'
        if not self.pools.is_empty():
            output += '\n**Dice Pools**\n'
            output += self.pools.output()
            output += '\n'
        if not self.xp.is_empty():
            output += '\n**Experience Points**\n'
            output += self.xp.output_all()
            output += '\n'
        return output

    def get_channel(self):
        return self.channel

    def get_option(self, key):
        value = None
        self.cursor.execute('SELECT * FROM GAME_OPTIONS WHERE PARENT_GUID=:game_guid AND KEY=:key', {'game_guid':self.db_guid, 'key':key})
        row = self.cursor.fetchone()
        if row:
            value = row['VALUE']
        return value

    def get_option_as_bool(self, key):
        as_bool = False
        value_str = self.get_option(key)
        if value_str:
            if value_str == 'on':
                as_bool = True
        return as_bool

    def set_option(self, key, value):
        prior = self.get_option(key)
        if not prior:
            new_guid = uuid.uuid1().hex
            self.cursor.execute('INSERT INTO GAME_OPTIONS (GUID, KEY, VALUE, PARENT_GUID) VALUES (?, ?, ?, ?)', (new_guid, key, value, self.db_guid))
        else:
            self.cursor.execute('UPDATE GAME_OPTIONS SET VALUE=:value where KEY=:key and PARENT_GUID=:game_guid', {'value':value, 'key':key, 'game_guid':self.db_guid})
        self.db.commit()

    def update_activity(self):
        self.cursor.execute('UPDATE GAME SET ACTIVITY=:now WHERE GUID=:db_guid', {'now':datetime.now(timezone.utc), 'db_guid':self.db_guid})
        self.db.commit()

class Roller:
    """Generates random die rolls and remembers the frequency of results."""

    def __init__(self):
        self.results = {}
        for size in DIE_SIZES:
            self.results[size] = [0] * size

    def roll(self, size):
        """Roll a die of a given size and return the result."""

        face = random.SystemRandom().randrange(1, int(size) + 1)
        self.results[size][face - 1] += 1
        return face

    def output(self):
        """Return a report of die roll frequencies."""

        total = 0

        frequency = ''
        separator = ''
        for size in self.results:
            subtotal = sum(self.results[size])
            total += subtotal
            frequency += '**{0}D{1}** : {2} rolls'.format(separator, size, subtotal)
            separator = '\n'
            if subtotal > 0:
                for face in range(1, size + 1):
                    frequency += ' : **{0}** {1}x {2}%'.format(
                        face,
                        self.results[size][face - 1],
                        round(float(self.results[size][face - 1]) / float(subtotal) * 100.0, 1))

        output = (
        '**Randomness**\n'
        'The bot has rolled {0} dice since starting up.\n'
        '\n'
        'Roll frequency statistics:\n'
        '{1}'
        ).format(total, frequency)

        return output

class Default(Controller):
    def GET(self):
        logger.info('GET')
        return "watch this space"

    def POST(self, **kwargs):
        logger.info('POST')
        logger.info(self.request.headers)

        response = None

        if verify_key(self.request.body.read(), self.request.headers['X-Signature-Ed25519'], self.request.headers['X-Signature-Timestamp'], config['discord']['public_key']):
            if kwargs['type'] == InteractionType.PING:
                logger.info('Responding to PING')
                response = DiscordResponsePong()
            else:
                self.db = sqlite3.connect(config['database']['file'])
                self.db.row_factory = sqlite3.Row
                self.roller = Roller()

                if kwargs['data']['name'] == 'info':
                    game = self.get_game_info(kwargs['guild_id'], kwargs['channel_id'])
                    response = self.info(game, kwargs['channel_id'])
                elif kwargs['data']['name'] == 'pin':
                    response = DiscordResponse('Pin command not yet implemented.')
                elif kwargs['data']['name'] == 'comp':
                    game = self.get_game_info(kwargs['guild_id'], kwargs['channel_id'])
                    response = self.comp(game, kwargs['data']['options'])
                elif kwargs['data']['name'] == 'pp':
                    game = self.get_game_info(kwargs['guild_id'], kwargs['channel_id'])
                    response = self.pp(game, kwargs['data']['options'])
                elif kwargs['data']['name'] == 'roll':
                    game = self.get_game_info(kwargs['guild_id'], kwargs['channel_id'])
                    response = self.roll(game, kwargs['data']['options'])
                else:
                    response = DiscordResponse(UNEXPECTED_ERROR)
        else:
            raise AccessDenied()
                
        logger.info(response.json())
        return response.json()

    def get_game_info(self, guild, channel, suppress_join=False):
        """Match a server and channel to a Cortex game."""
        game_info = None
        fallback_game = None
        game_key = [guild, channel]
        joined_channel = None
        while not game_info:
            game_info = CortexGame(self.db, game_key[0], game_key[1])
            if joined_channel:
                if game_info.get_option(JOIN_OPTION) != 'on':
                    joined_channel_name = 'other'
                    for channel in context.guild.channels:
                        if channel.id == game_key[1]:
                            joined_channel_name = channel.name
                    game_info = fallback_game
                    game_info.set_option(JOIN_OPTION, 'off')
                    raise CortexError(JOIN_ERROR, joined_channel_name)
            elif not suppress_join:
                joined_channel = game_info.get_option(JOIN_OPTION)
                if joined_channel and joined_channel != 'on' and joined_channel != 'off':
                    fallback_game = game_info
                    game_info = None
                    game_key = [context.guild.id, int(joined_channel)]
        return game_info

    def info(self, game, origin_channel):
        """Display all game information."""

        try:
            game.update_activity()
            output = game.output()
            if game.get_channel() != origin_channel:
                output = output.replace(GAME_INFO_HEADER, GAME_INFO_HEADER + '\n(from joined channel)')
                '''
                for channel in ctx.guild.channels:
                    if channel.id == game.get_channel():
                        output = output.replace(GAME_INFO_HEADER, GAME_INFO_HEADER + '\n(from channel #{0})'.format(channel.name))
                '''
            return DiscordResponse(output)
        except CortexError as err:
            return DiscordResponse(err)
        except:
            logging.error(traceback.format_exc())
            return DiscordResponse(UNEXPECTED_ERROR)

    def comp(self, game, options):
        logging.debug("comp command invoked")
        try:
            output = ''
            game.update_activity()
            comp_name = capitalize_words(options[0]['options'][0]['value'])
            if options[0]['name'] == 'add':
                dice = parse_string_into_dice(options[0]['options'][1]['value'])
                if not dice:
                    raise CortexError(DIE_MISSING_ERROR)
                elif len(dice) > 1:
                    raise CortexError(DIE_EXCESS_ERROR)
                elif dice[0].qty > 1:
                    raise CortexError(DIE_EXCESS_ERROR)
                output = game.complications.add(comp_name, dice[0])
            elif options[0]['name'] == 'remove':
                output = game.complications.remove(comp_name)
            elif args[0] in UP_SYNONYMS:
                output = game.complications.step_up(comp_name)
            elif args[0] in DOWN_SYNONYMS:
                output = game.complications.step_down(comp_name)
            else:
                raise CortexError(INSTRUCTION_ERROR, options[0], 'comp')
            return DiscordResponse(output)
        except CortexError as err:
            return DiscordResponse(err)
        except:
            logging.error(traceback.format_exc())
            return DiscordResponse(UNEXPECTED_ERROR)

    def pp(self, game, options):
        logging.debug("pp command invoked")
        try:
            output = ''
            update_pin = False
            game.update_activity()
            char_name = capitalize_words(options[0]['options'][0]['value'])
            if options[0]['name'] == 'add':
                output = 'Plot points for ' + game.plot_points.add(char_name, qty)
            elif options[0]['name'] == 'remove':
                output = 'Plot points for ' + game.plot_points.remove(char_name, qty)
            elif options[0]['name'] == 'clear':
                output = game.plot_points.clear(char_name)
            else:
                raise CortexError(INSTRUCTION_ERROR, options[0], 'pp')
            return DiscordResponse(output)
        except CortexError as err:
            return DiscordResponse(err)
        except:
            logging.error(traceback.format_exc())
            return DiscordResponse(UNEXPECTED_ERROR)

    def roll(self, game, options):
        logging.debug("roll command invoked")
        results = {}
        try:
            suggest_best = game.get_option_as_bool(BEST_OPTION)
            dice = parse_string_into_dice(options[0]['value'])
            pool = DicePool(self.db, None, incoming_dice=dice)
            echo_line = 'Rolling: {0}\n'.format(pool.output())
            return DiscordResponse(echo_line + pool.roll(self.roller, suggest_best))
        except CortexError as err:
            return DiscordResponse(err)
        except:
            logging.error(traceback.format_exc())
            return DiscordResponse(UNEXPECTED_ERROR)
