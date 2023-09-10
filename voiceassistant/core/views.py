from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.db import IntegrityError
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from core.chatgpt import get_chat_response
import googletrans
from googletrans import Translator  # Install the googletrans library

class ChatbotView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = ConversationSerializer(data=request.data, context = {'request': request})

        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            input_text = serializer.validated_data['input_text']
            conversation_id = serializer.validated_data.get('conversation_id')
            language_pref = serializer.validated_data['language']

            message_user_type = 1 #user
            message_type = 1 #text

            # Check if a conversation with the provided ID exists; if not, create a new one
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    conversation = Conversation.objects.create(user_id=user_id)
                except IntegrityError as e:
                    return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

            messages = []

            # Create a new message within the conversation
            message_data = {
                'conversation_id': conversation.id,
                'type': message_type,
                'content': input_text,
                'message_user_type': message_user_type,
                'user_id': user_id
            }
            message_serializer = MessageSerializer(data=message_data)

            # Check if the message data is valid according to the MessageSerializer
            if message_serializer.is_valid():
                message_serializer.save()
                messages.append(message_serializer.validated_data)

                assistant_reply = get_chat_response(input_text)

                translator = Translator()
                translated_response = translator.translate(assistant_reply, dest=language_pref).text

                message_user_type = 2 #Bot

                # Create a response message and save it to the database
                response_data = {
                    'conversation_id': conversation.id,
                    'type': message_type,
                    'content': translated_response,
                    'message_user_type': message_user_type, 
                    'user_id': user_id
                }
                response_serializer = MessageSerializer(data=response_data)

                # Check if the response data is valid according to the MessageSerializer
                if response_serializer.is_valid():
                    response_serializer.save()
                    messages.append(response_serializer.validated_data)
                    response_data = {
                        'conversation_id': conversation.id,
                        'messages': messages 
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)