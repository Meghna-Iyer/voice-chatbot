from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from django.db import IntegrityError
from django.db.models import F
from django.http import Http404
from .models import Conversation, Message, User
from .serializers import ConversationTextSerializer, ConversationVoiceSerializer, MessageSerializer, ConversationListSerializer, MessageListSerializer, ConversationUpdateSerializer, TextToSpeechSerializer
from core.chatgpt import getChatGptResponse, getConversationTitle
from core.voice import getTextFromAudio, getAudioFromText
from core.language import translate
from core.enums import MessageType, MessageUserType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import threading

class ChatbotBaseView(APIView):
    
    def getOrCreateConversation(self, conversation_id, user):
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                isNew = False
            except Conversation.DoesNotExist:
                raise Exception('Conversation not found')
        else:
            try:
                conversation = Conversation.objects.create(user_id=user.id)
                isNew = True;
            except IntegrityError as e:
                raise Exception('User not found')
    
        return conversation, isNew

    def getUpdatedConversation(self, conversation, user_id, text, shouldAutoUpdateTitle):
        
        if shouldAutoUpdateTitle:
            title = getConversationTitle(text)
            Conversation.objects.filter(id=conversation.id,user_id=user_id).update(title=title)
            conversation.title = title

        return conversation

    def getUser(self, user_id):
        user = User.objects.get(id=user_id)
        return user

    def createAndAddMessage(self, conversation, message_type, content, message_user_type, user_id, messages, reference=None, file_name=None):
        message_data = {
            'conversation_id': conversation.id,
            'type': message_type,
            'content': content,
            'reference': reference,
            'file_name': file_name,
            'message_user_type': message_user_type,
            'user_id': user_id
        }

        if MessageType.TEXT.value == message_type:
            del message_data['reference']
            del message_data['file_name']
        else:
            del message_data['content']
        
        message_serializer = MessageSerializer(data=message_data)

        if message_serializer.is_valid():
            message_serializer.save()
            data = message_serializer.data
            # handle uuid field
            data['message_id'] = str(data['message_id']) 
            self.sendMsgViaWS(conversation.id, data)
            messages.append(data)
        else:
            print(message_serializer.errors)
            raise Exception(message_serializer.errors)
        
    def sendMsgViaWS(self, conversation_id, message):
         channel_layer = get_channel_layer()
         async_to_sync(channel_layer.group_send)(
             f"chat_{conversation_id}",
             {
                'type': 'chat.message',
                'message': message
             }
         )
    
    def process_bot_response(self, input_text, conversation, messages, user):
        language_pref = user.lang_preference
        user_id = user.id
        use_chat_history = user.use_chat_history
        conversation_id = conversation.id

        try:
            
            assistant_reply = getChatGptResponse(input_text, use_chat_history, user_id, conversation_id)
            translated_response = translate(assistant_reply, dest=language_pref)
            
            message_user_type = MessageUserType.BOT.value
            message_type = MessageType.TEXT.value

            self.createAndAddMessage(conversation, message_type, translated_response, message_user_type, user_id, messages)

        except Exception as e:
            print(f"Error in async_process_bot_response: {str(e)}")


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

            message_user_type = MessageUserType.USER.value
            message_type = MessageType.TEXT.value

            try:

                conversation, isNewConversation = self.getOrCreateConversation(conversation_id, user)
                conversation = self.getUpdatedConversation(conversation, user_id, input_text, isNewConversation)

                messages = []

                self.createAndAddMessage(conversation, message_type, input_text, message_user_type, user_id, messages)

                if isNewConversation:
                    self.process_bot_response(input_text, conversation, messages, user)
                else:  
                    thread = threading.Thread(target=self.process_bot_response, args=(input_text, conversation, messages, user))
                    thread.start()

                conversation_serializer = ConversationUpdateSerializer(conversation)
                response_data = {
                    'conversation': conversation_serializer.data,
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

    def updateContentForAudio(self, messages, content):
        Message.objects.filter(id=messages[0]["message_id"]).update(content=content)
        messages[0]["content"] = content

    def post(self, request):
        serializer = ConversationVoiceSerializer(data=request.data, context = {'request': request})

        if serializer.is_valid():

            user_id = self.request.user.id
            user = self.getUser(user_id)
            audio = serializer.validated_data['audio']
            conversation_id = serializer.validated_data.get('conversation_id')
            audio_name = audio.name

            message_user_type = MessageUserType.USER.value
            message_type = MessageType.AUDIO.value

            conversation, isNewConversation = self.getOrCreateConversation(conversation_id, user)

            messages = []

            try:
                self.createAndAddMessage(conversation, message_type, None, message_user_type, user_id, messages, audio, audio_name)

                input_text = getTextFromAudio(messages[0]["reference"])['text']

                self.updateContentForAudio(messages, input_text)
                conversation = self.getUpdatedConversation(conversation, user_id, input_text, isNewConversation)

                if isNewConversation:
                    self.process_bot_response(input_text, conversation, messages, user)
                else:  
                    thread = threading.Thread(target=self.process_bot_response, args=(input_text, conversation, messages, user))
                    thread.start()

                conversation_serializer = ConversationUpdateSerializer(conversation)
                response_data = {
                    'conversation': conversation_serializer.data,
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
        return Conversation.objects.filter(user_id=user_id).order_by(F('created').desc())
    
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
        return Message.objects.filter(conversation__id=conversation_id).order_by(F('created').desc())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        messages = serializer.data

        response_data = {
            'messages': messages,
        }
        return Response(response_data)
  

class ConversationUpdateDeleteView(generics.DestroyAPIView, generics.UpdateAPIView):
    parser_classes = [JSONParser]
    serializer_class = ConversationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        conversation_id = self.kwargs['pk']
        return Conversation.objects.filter(id=conversation_id, user_id=user_id)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.first()

        if obj is None:
            raise Http404("No conversations found")
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Conversations deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


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
