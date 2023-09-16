from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import ChatbotTextView, ChatbotVoiceView, ConversationListView, MessageListView, TextToSpeechView


app_name = 'core'

urlpatterns = [
    path('chatbot/text', ChatbotTextView.as_view(), name='chatbot-text'),
    path('chatbot/voice', ChatbotVoiceView.as_view(), name='chatbot-voice'),
    path('conversations/<uuid:user_id>/', ConversationListView.as_view(), name='conversation-list'),
    path('messages/<uuid:conversation_id>/', MessageListView.as_view(), name='message-list'),
    path("text-to-speech/", TextToSpeechView.as_view(), name="text-to-speech"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)