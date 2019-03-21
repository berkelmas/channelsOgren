# chat/consumers.py
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

from .models import Message

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):     ## Burada daha önceki gemiş 10 mesajımızı kullanıcıya getireceğiz.
        messages = Message.objects.order_by('-timestamp').all()[:10]    ## DB'den ilk 10 mesjaı alıyoruz.
        content = {
            'messages' : self.messages_to_json(messages)
        }
        self.add_messages_from_db(content)

    def new_message(self, data):
        self.send_text_message(data)

    ## Burada mesaj db'mizdeki mesajlarımızı; JSON objelerine dönüştürerek geri dönüyoruz.
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.single_message_to_json(message))
        return result

    def single_message_to_json(self, message):
        json_message = {
            'author' : message.author.username,
            'content' : message.content,
            'timestamp' : str(message.timestamp)
        }
        return json_message

    commands = {
        'fetch_messages' : fetch_messages,
        'new_message' : new_message
    }

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
        data = json.loads(text_data)                 ## Burada WebSocket'ten aldığı string şeklindeki JSON datasını Python Dictionary'sine çeviriyoruz.
        self.commands[data['command']](self, data)   ## Burada WebSocket'ten ne aldığımzı command isteğine göre fetch veya new message fonksiyonlarımızı çalıştırıyoruz.


    ## Burada group_send() metodunu kullanma nedenimiz; buradaki mesajın tüm grup üyelerine dağıtılmasını istememiz.
    def send_text_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'gruba_gonder',
                'message': message
            }
        )


    # Açılışta WebSocket'in bizden geçmiş son 10 mesaj isteğini back-end'de çözdükten sonra tekrar fronta iletiyoruz.
    # Burada direk send() metodunu kullanma nedenimiz; diğer chat odası üyelerine mesajı iletmemize gerek olmayışı.
    def add_messages_from_db(self, messages):
        self.send(text_data=json.dumps(messages))


    # Aldığımız mesajı tekrar client side'a burada iletiyoruz.
    def gruba_gonder(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

