import uuid
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Conversation, Message

class ConversationTextSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(default=uuid.uuid4)
    input_text = serializers.CharField()
    conversation_id = serializers.UUIDField(required=False)
    language = serializers.CharField()

    class Meta:
        model = Conversation
        fields = '__all__'


class ConversationVoiceSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(default=uuid.uuid4)
    audio = serializers.FileField()
    conversation_id = serializers.UUIDField(required=False)
    language = serializers.CharField()

    def validate(self, attrs):
        supported_extensions = ['mp3', 'wav', 'ogg']
        file_extension = attrs.get('audio').name.split('.')[-1].lower()
        print(file_extension)
        if not any(file_extension.endswith(ext) for ext in supported_extensions):
            raise ValidationError(f"Unsupported file format. Supported formats are {', '.join(supported_extensions)}")
        return attrs

    class Meta:
        model = Conversation
        fields = '__all__'

class ConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

class MessageSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(default=uuid.uuid4)
    conversation_id = serializers.UUIDField(default=uuid.uuid4)
    content = serializers.CharField()
    type = serializers.IntegerField()
    reference = serializers.FileField(required=False)
    message_user_type = serializers.IntegerField()

    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        instance = Message(**validated_data)
        instance.save()
        return instance
    
class FileFieldURL(serializers.FileField):
    def to_representation(self, value):
        if value:
            return value.url
        return None

class MessageListSerializer(serializers.ModelSerializer):
    reference = FileFieldURL()
    class Meta:
        model = Message
        fields = '__all__' 

class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField()
    language = serializers.CharField()