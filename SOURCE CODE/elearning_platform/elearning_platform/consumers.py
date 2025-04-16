import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class MeetingConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user_info(self, user):
        return user.userinfo # logic to get user info
    
    async def connect(self):
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"meeting_{self.room_name}"
        print(f"User {self.scope['user']} is attempting to join room {self.room_group_name}")

        # join the WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        print(f"User {self.scope['user']} added to {self.room_group_name}")

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "type": "user_left",
            "name": self.scope["user"].userinfo.display_name
        }))

    # receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        name = text_data_json.get('name', 'Anonymous')
        message_type = text_data_json.get('type', '')

        if message_type == 'end_meeting':
            # if the message is to end the meeting, call the end_meeting method
            await self.end_meeting()
        
        else:
            # otherwise, handle other types of messages (like chat messages)
            message = text_data_json.get('message', '')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'name': name,
                    'message': message
                }
            )

    # receive message from group
    async def chat_message(self, event):
        name = event['name']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'name': name,
            'message': message
        }))

    async def end_meeting(self):
        # logic to notify all participants that the meeting is ending
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'meeting_ended',
            }
        )

    async def meeting_ended(self, event):
        # notify the client that the meeting is ended
        await self.send(text_data=json.dumps({
            'message': 'The meeting has ended. Redirecting...',
            'redirect': True
        }))
        # close the connection (disconnect the client)
        await self.close()
