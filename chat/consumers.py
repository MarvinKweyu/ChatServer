import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    """
    This is a synchronous WebSocket consumer that accepts all connections
    """
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f'chat_{self.room_name}'

        # join group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )


    def receive(self, text_data):
        """
        Reveive message from web socket
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # send message to a room group
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        """
        Receive message from room group
        """
        message = event['message']

        # send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))