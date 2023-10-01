import json
from channels.generic.websocket import AsyncWebsocketConsumer

    
class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the websocket connection
        print("Accepting Connection....")
        self.conv_id = self.scope['url_route']['kwargs']['conv_id']
        self.conv_group_name = f"chat_{self.conv_id}"

        # Join group
        await self.channel_layer.group_add(
            self.conv_group_name, 
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        self.conv_group_name = f"chat_{self.conv_id}"
        await self.channel_layer.group_discard(
			self.conv_group_name,
			self.channel_name
		)
        # Close the websocket connection
        await self.close()

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
