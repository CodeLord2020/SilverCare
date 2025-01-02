
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from messaging.consumers import ChatConsumer
from messaging.models import Conversation
import json
from django.contrib.auth import get_user_model



class ChatConsumerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    async def test_chat_consumer_connect(self):
        # Create auth headers
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
            headers=[(
                b"cookie",
                f"sessionid={self.client.session.session_key}".encode()
            )]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_chat_consumer_send_receive(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{self.conversation.id}/",
            headers=[(
                b"cookie",
                f"sessionid={self.client.session.session_key}".encode()
            )]
        )
        await communicator.connect()
        
        # Send a test message
        await communicator.send_json_to({
            'message': 'Test message'
        })
        
        # Receive response
        response = await communicator.receive_json_from()
        self.assertEqual(response['message'], 'Test message')
        
        await communicator.disconnect()