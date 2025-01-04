import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from .models import Conversation,Message, UnreadMessageCounter

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        print(f"Channel Layer: {self.channel_layer}") 

        if not await self.has_conversation_access():
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        print(f"Received data: {text_data}")  # Debug
        text_data_json = json.loads(text_data)
        if 'type' in text_data_json and text_data_json['type'] == 'typing':
            # Handle typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user_id': str(self.scope['user'].id),
                    'is_typing': True
                }
            )
        elif 'message' in text_data_json:
            # Handle regular message
            message = text_data_json['message']
            saved_message = await self.save_message(message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': str(self.scope['user'].id),
                    'message_id': str(saved_message.id),
                    'timestamp': saved_message.created_at.isoformat()
                }
            )


    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))
    async def message_delivery_status(self, event):
        """Send message delivery status to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'delivery_status',
            'message_id': event['message_id'],
            'status': event['status']
        }))


    @database_sync_to_async
    def has_conversation_access(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            user = self.scope['user']
            return (
                user == conversation.elder or 
                user == conversation.helper
            ) and conversation.is_active
        except ObjectDoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=self.scope['user'],
            content=content
        )


    # async def typing_status(self, event):
    #     """Send typing status to WebSocket"""
    #     await self.send(text_data=json.dumps({
    #         'type': 'typing_status',
    #         'user_id': event['user_id'],
    #         'is_typing': event['is_typing']
    #     }))

    # async def receive_typing(self, text_data):
    #     """Handle typing indicator updates"""
    #     try:
    #         data = json.loads(text_data)
    #         if data.get('type') == 'typing':
    #             await self.channel_layer.group_send(
    #                 self.room_group_name,
    #                 {
    #                     'type': 'typing_status',
    #                     'user_id': str(self.scope['user'].id),
    #                     'is_typing': True
    #                 }
    #             )
    #     except json.JSONDecodeError:
    #         pass

