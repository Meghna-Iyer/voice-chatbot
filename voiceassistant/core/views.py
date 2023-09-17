from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from django.db import IntegrityError
from .models import Conversation, Message, User
from .serializers import ConversationTextSerializer, ConversationVoiceSerializer, MessageSerializer, ConversationListSerializer, MessageListSerializer, TextToSpeechSerializer
from core.chatgpt import getChatGptResponse
from core.voice import getTextFromAudio, getAudioFromText
from core.language import translate

class ChatbotBaseView(APIView):
    
    def getOrCreateConversation(self, conversation_id, user):
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                raise Exception('Conversation not found')
        else:
            try:
                title = "Conversation With " + user.first_name
                conversation = Conversation.objects.create(user_id=user.id, title=title)
            except IntegrityError as e:
                raise Exception('User not found')
    
        return conversation


    def getUser(self, user_id):
        user = User.objects.get(id=user_id)
        return user


    def createAndAddMessage(self, conversation, message_type, content, message_user_type, user_id, messages, reference=None):
        message_data = {
            'conversation_id': conversation.id,
            'type': message_type,
            'content': content,
            'reference': reference,
            'message_user_type': message_user_type,
            'user_id': user_id
        }

        # text messages would not contain reference
        if reference is None:
            del message_data['reference']
        
        message_serializer = MessageSerializer(data=message_data)

        if message_serializer.is_valid():
            output = message_serializer.save()
            validated_data = message_serializer.validated_data
            
            # save url in ref
            if validated_data.get("reference"):
                validated_data["reference"] = output.reference.url
            
            messages.append(validated_data)
        else:
            print(message_serializer.errors)
            raise Exception(message_serializer.errors)


class ChatbotTextView(ChatbotBaseView):
    parser_classes = [JSONParser]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ConversationTextSerializer(data=request.data, context = {'request': request})

        if serializer.is_valid():
            
            user_id = self.request.user.id
            user = self.getUser(user_id)
            input_text = serializer.validated_data['input_text']
            conversation_id = serializer.validated_data.get('conversation_id')
            language_pref = user.lang_preference

            message_user_type = 1 #user
            message_type = 1 #text

            try:

                conversation = self.getOrCreateConversation(conversation_id, user)

                messages = []

                self.createAndAddMessage(conversation, message_type, input_text, message_user_type, user_id, messages)

                assistant_reply = getChatGptResponse(input_text)

                translated_response = translate(assistant_reply, dest=language_pref)

                message_user_type = 2 #Bot
                message_type = 1 #text

                self.createAndAddMessage(conversation, message_type, translated_response, message_user_type, user_id, messages)

                response_data = {
                    'conversation_id': conversation.id,
                    'messages': messages
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ChatbotVoiceView(ChatbotBaseView):
    parser_classes = [MultiPartParser]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ConversationVoiceSerializer(data=request.data, context = {'request': request})

        if serializer.is_valid():

            user_id = self.request.user.id
            user = self.getUser(user_id)
            audio = serializer.validated_data['audio']
            conversation_id = serializer.validated_data.get('conversation_id')
            language_pref = user.lang_preference
            audio_name = audio.name

            message_user_type = 1 #user
            message_type = 2 #audio

            conversation = self.getOrCreateConversation(conversation_id, user)

            messages = []

            try:
                self.createAndAddMessage(conversation, message_type, audio_name, message_user_type, user_id, messages, audio)

                input_text = getTextFromAudio(messages[0]["reference"])['text']

                print(input_text)
                assistant_reply = getChatGptResponse(input_text)

                translated_response = translate(assistant_reply, dest=language_pref)

                message_type = 1 #text
                message_user_type = 2 #Bot

                self.createAndAddMessage(conversation, message_type, translated_response, message_user_type, user_id, messages)

                response_data = {
                    'conversation_id': conversation.id,
                    'messages': messages
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationListView(generics.ListAPIView):
    parser_classes = [JSONParser]
    serializer_class = ConversationListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.request.user.id
        return Conversation.objects.filter(user_id=user_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        conversations = serializer.data
        response_data = {
            "conversations": conversations
        }
        return Response(response_data)


class MessageListView(generics.ListAPIView):
    parser_classes = [JSONParser]
    serializer_class = MessageListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation__id=conversation_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        messages = serializer.data

        # Modify the reference URLs if necessary
        for message in messages:
            if message['reference']:
                message['reference'] = request.build_absolute_uri(message['reference'])

        response_data = {
            'messages': messages,
        }
        return Response(response_data)
  

class TextToSpeechView(ChatbotBaseView):
    parser_classes = [JSONParser]
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = TextToSpeechSerializer(data=request.data)
        
        if serializer.is_valid():
            text = serializer.validated_data["text"]
            language = self.getUser(self.request.user.id).lang_preference

            audio_data = getAudioFromText(text=text, language=language)

            return Response({"audio_base64": audio_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
