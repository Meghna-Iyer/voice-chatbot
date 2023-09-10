from django.urls import path

from .views import ChatbotView


app_name = 'core'

urlpatterns = [
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
]