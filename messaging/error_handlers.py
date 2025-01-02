
from channels.exceptions import DenyConnection
from django.core.exceptions import ValidationError
import logging, json

logger = logging.getLogger(__name__)

class WebSocketErrorHandler:
    @staticmethod
    async def handle_connection_error(consumer, error):
        logger.error(f"WebSocket connection error: {error}")
        await consumer.close()

    @staticmethod
    async def handle_message_error(consumer, error):
        logger.error(f"Message handling error: {error}")
        await consumer.send(text_data=json.dumps({
            'type': 'error',
            'message': 'Failed to process message'
        }))