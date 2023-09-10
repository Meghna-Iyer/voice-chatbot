from django.db import models
from utils.model_abstracts import Model
from django.contrib.auth.models import AbstractUser
from django_extensions.db.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel, Model):
    user_type = user_type = models.PositiveSmallIntegerField()
    lang_preference = models.CharField(default='en', max_length=5)