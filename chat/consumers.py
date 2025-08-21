import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

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

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']

        # Save message to database
        await self.save_message(username, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )
        
        # Send notification to recipient
        await self.send_notification(room, username, message)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
    
    # Send notification to recipient
    @sync_to_async
    def send_notification(self, room_id, sender_username, message):
        room = ChatRoom.objects.get(id=room_id)
        sender = User.objects.get(username=sender_username)
        
        # Find recipient (the other user in the chat)
        recipient = None
        for participant in room.participants.all():
            if participant != sender:
                recipient = participant
                break
        
        if recipient:
            # Send notification to recipient's personal channel
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            recipient_channel_name = f"user_{recipient.id}"
            
            async_to_sync(channel_layer.group_send)(
                recipient_channel_name,
                {
                    'type': 'notification_message',
                    'message': message,
                    'sender': sender_username,
                    'notification_type': 'new_message'
                }
            )

    # Handle notifications
    async def notification_message(self, event):
        message = event['message']
        sender = event['sender']
        notification_type = event['notification_type']
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
            'sender': sender,
            'notification_type': notification_type
        }))

    @sync_to_async
    def save_message(self, username, room_id, message):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(id=room_id)
        Message.objects.create(room=room, sender=user, content=message)