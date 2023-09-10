import uuid
from rest_framework import serializers
from .models import Conversation, Message

class ConversationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(default=uuid.uuid4)
    input_text = serializers.CharField()
    conversation_id = serializers.UUIDField(required=False)
    language = serializers.CharField()

    class Meta:
        model = Conversation
        fields = '__all__'


class MessageSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(default=uuid.uuid4)
    conversation_id = serializers.UUIDField(default=uuid.uuid4)
    content = serializers.CharField()
    type = serializers.IntegerField()
    message_user_type = serializers.IntegerField()

    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        instance = Message(**validated_data)
        instance.save()
        return instance   