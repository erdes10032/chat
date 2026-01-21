from django.urls import path
from .views import ChatListView, ChatDetailView, MessageCreateView

urlpatterns = [
    # Создание чата
    path('chats/', ChatListView.as_view(), name='chat-list'),

    # Получение и удаление чата
    path('chats/<int:id>/', ChatDetailView.as_view(), name='chat-detail'),

    # Отправка сообщения в чат
    path('chats/<int:id>/messages/', MessageCreateView.as_view(), name='message-create'),
]