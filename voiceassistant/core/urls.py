from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import ChatbotTextView, ChatbotVoiceView


app_name = 'core'

urlpatterns = [
    path('chatbot/text', ChatbotTextView.as_view(), name='chatbot-text'),
    path('chatbot/voice', ChatbotVoiceView.as_view(), name='chatbot-voice'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)