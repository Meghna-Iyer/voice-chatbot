import uuid
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Conversation, Message
from core.enums import MessageType, MessageUserType

class ConversationTextSerializer(serializers.Serializer):
    input_text = serializers.CharField()
    conversation_id = serializers.UUIDField(required=False)

    class Meta:
        model = Conversation
        fields = '__all__'


class ConversationVoiceSerializer(serializers.Serializer):
    audio = serializers.FileField()
    conversation_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        supported_extensions = ['mp3', 'wav', 'ogg']
        file_extension = attrs.get('audio').name.split('.')[-1].lower()
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


class ConversationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'title']


class MessageSerializer(serializers.Serializer):
    message_id = serializers.UUIDField(required=False)
    user_id = serializers.UUIDField(default=uuid.uuid4)
    conversation_id = serializers.UUIDField(default=uuid.uuid4)
    content = serializers.CharField(required=False)
    type = serializers.ChoiceField(choices=[(m.value, m.name) for m in MessageType])
    message_user_type = serializers.ChoiceField(choices=[(u.value, u.name) for u in MessageUserType])
    reference = serializers.FileField(required=False)
    file_name = serializers.CharField(required=False)

    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        instance = Message(**validated_data)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['type'] = MessageType(instance.type).name
        representation['message_user_type'] = MessageUserType(instance.message_user_type).name
        representation['message_id'] = instance.id
        if 'reference' in representation and instance.reference:
            representation['reference'] = instance.reference.url
        return representation


class MessageListSerializer(serializers.ModelSerializer):
    reference = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_reference(self, obj):
        if obj.reference:
            return obj.reference.url
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['type'] = MessageType(instance.type).name
        representation['message_user_type'] = MessageUserType(instance.message_user_type).name
        return representation


class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField()