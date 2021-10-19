import os
import logging
import logging.handlers
import configparser
from endpoints.interface.wsgi import Application

config = configparser.ConfigParser()
config.read('cortexpal.ini')

logHandler = logging.handlers.TimedRotatingFileHandler(filename=config['logging']['file'], when='D', backupCount=9)
logging.basicConfig(handlers=[logHandler], format='%(asctime)s %(message)s', level=logging.DEBUG)

os.environ['ENDPOINTS_PREFIX'] = 'CortexPal'
application = Application()

