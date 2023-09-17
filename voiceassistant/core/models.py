from django.db import models
from utils.model_abstracts import Model
from django_extensions.db.models import (
    TimeStampedModel,
    ActivatorModel,
    TitleSlugDescriptionModel
)
from user.models import User
from core.enums import MessageType, MessageUserType


class Conversation(Model, TimeStampedModel, ActivatorModel, TitleSlugDescriptionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Message(Model, TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=[(m.value, m.name) for m in MessageType])
    content = models.TextField()
    reference = models.FileField(upload_to="audio/", blank=True)
    message_user_type = models.PositiveSmallIntegerField(choices=[(u.value, u.name) for u in MessageUserType])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
