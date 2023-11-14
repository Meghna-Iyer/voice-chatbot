from django.db import models
from utils.model_abstracts import Model
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel
)
from user.models import User
from core.enums import MessageType, MessageUserType
import os
from uuid import uuid4


class Conversation(Model, TimeStampedModel, ActivatorModel, TitleSlugDescriptionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)


def generate_audio_filename(instance, filename):
    user_id = instance.user_id
    conversation_id = instance.conversation_id

    unique_filename = uuid4().hex
    
    folder_path = os.path.join("audio", f"user_{user_id}", f"conv_{conversation_id}")
    
    return os.path.join(folder_path, f"{unique_filename}_{filename}")


class Message(Model, TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=[(m.value, m.name) for m in MessageType])
    content = models.TextField(blank=True)
    reference = models.FileField(upload_to=generate_audio_filename, blank=True, max_length=255)
    message_user_type = models.PositiveSmallIntegerField(choices=[(u.value, u.name) for u in MessageUserType])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.TextField(blank=True)
