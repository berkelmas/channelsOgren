from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Message

admin.site.register(Message)
