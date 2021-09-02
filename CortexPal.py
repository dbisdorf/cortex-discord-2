from endpoints import Controller, AccessDenied
from discord_interactions import verify_key, InteractionType, InteractionResponseType
import logging
import json

PUBLIC_KEY = '49c8cfe5c6f482f93a96ab2c82b97b97a6f68b665d8b3a5871b3c0ed58dc2239'
logger = logging.getLogger(__name__)

class Default(Controller):
    def GET(self):
        logger.info('GET')
        return "watch this space"

    def POST(self, **kwargs):
        logger.info('POST')
        logger.info(self.request.headers)

        response = {}

        if verify_key(self.request.body.read(), self.request.headers['X-Signature-Ed25519'], self.request.headers['X-Signature-Timestamp'], PUBLIC_KEY):
            if kwargs['type'] == InteractionType.PING:
                logger.info('Responding to PING')
                response = {"type": InteractionResponseType.PONG}
        else:
            raise AccessDenied()
                
        logger.info(response)
        return response

