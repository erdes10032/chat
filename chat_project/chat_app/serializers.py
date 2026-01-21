from rest_framework import serializers
from .models import Chat, Message


class ChatSerializer(serializers.ModelSerializer):
    """Сериализатор для чата."""

    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_title(self, value):
        """Тримминг пробелов"""
        if isinstance(value, str):
            return value.strip()
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщения."""

    class Meta:
        model = Message
        fields = ['id', 'chat', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_text(self, value):
        """Тримминг пробелов"""
        if isinstance(value, str):
            return value.strip()
        return value


class ChatDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о чате с сообщениями."""
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at', 'messages']