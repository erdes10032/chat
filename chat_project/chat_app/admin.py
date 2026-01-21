from django.contrib import admin
from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'created_at', 'text_preview')
    list_filter = ('created_at', 'chat')
    search_fields = ('text', 'chat__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def text_preview(self, obj):
        """Превью текста сообщения."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Текст (превью)'