from django.contrib.auth.models import User
from django.db import models

class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username + '' + self.content

    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]


