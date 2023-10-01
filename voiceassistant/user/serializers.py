from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    USER_TYPES = (
        (0, 'Admin'),
        (1, 'Agent'),
        (2, 'User'),
    )
    user_type = serializers.ChoiceField(choices=USER_TYPES)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'user_type', 'lang_preference')

    @staticmethod
    def clean_validated_data(validated_data):
        validated_data.pop('confirm_password')
        return validated_data

    def validate(self, attrs):
        validate_password(attrs.get('password'))

        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('password and confirm password do not match!')

        return attrs

    def create(self, validated_data):
        user = self.Meta.model.objects.create_user(**self.clean_validated_data(validated_data))
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'lang_preference', 'use_chat_history')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'lang_preference', 'use_chat_history')