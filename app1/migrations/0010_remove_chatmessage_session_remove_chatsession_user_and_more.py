# Generated by Django 5.2 on 2025-04-11 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0009_chatsession_chatmessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='session',
        ),
        migrations.RemoveField(
            model_name='chatsession',
            name='user',
        ),
        migrations.DeleteModel(
            name='Knowledge',
        ),
        migrations.DeleteModel(
            name='ChatMessage',
        ),
        migrations.DeleteModel(
            name='ChatSession',
        ),
    ]
