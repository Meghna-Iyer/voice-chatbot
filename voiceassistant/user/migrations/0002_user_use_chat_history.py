# Generated by Django 4.1.3 on 2023-10-01 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='use_chat_history',
            field=models.BooleanField(default=False),
        ),
    ]
