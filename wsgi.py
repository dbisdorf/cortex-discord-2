import os
import logging
import logging.handlers
from endpoints.interface.wsgi import Application

logHandler = logging.handlers.TimedRotatingFileHandler(filename='/home/don/cortex-dev/logs/dev.log', when='D', backupCount=9)
logging.basicConfig(handlers=[logHandler], format='%(asctime)s %(message)s', level=logging.DEBUG)

os.environ['ENDPOINTS_PREFIX'] = 'CortexPalSlash'
application = Application()

