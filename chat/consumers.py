# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class ChatConsumer(WebsocketConsumer):
    def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    ## Web Socket'ten mesajı almak için fonksiyon
    def receive(self, text_data):
        text_data_json = json.loads(text_data)    ## Burada WebSocket'ten aldığı string şeklindeki JSON datasını Python Dictionary'sine çeviriyoruz.
        message = text_data_json['message']       ## JavaScript içerisinde bu datamızı { 'message' : message } olarak çağırdığımızdan; message kısmını JSON datamızın içerisinden alıyoruz.

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'gruba_gonder',
                'message': message
            }
        )
        """
        self.send(text_data=json.dumps({          ## Aldığımız JSON datasını tekrar BackEnd'den FrontEnd'e gönderirken; json.dumps() metodu ile string'e çeviriyoruz.
            'message': message
        }))
        """

    # Receive message from room group
    def gruba_gonder(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

