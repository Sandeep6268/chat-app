import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_authenticated:
            self.room_group_name = f'user_{self.user.id}'
            
            # Join user's personal notification group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave user's personal notification group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive notification from group
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