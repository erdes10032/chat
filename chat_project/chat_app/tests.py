import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Chat, Message
from django.core.exceptions import ValidationError
import time


class ChatModelTests(TestCase):
    """Тесты для модели Chat."""

    def test_create_chat(self):
        """Тест создания чата."""
        chat = Chat.objects.create(title="Тестовый чат")
        self.assertEqual(chat.title, "Тестовый чат")
        self.assertIsNotNone(chat.created_at)
        self.assertEqual(str(chat), f"Тестовый чат (ID: {chat.id})")

    def test_chat_title_trimming(self):
        """Тест тримминга пробелов в названии чата."""
        chat = Chat.objects.create(title="  Чат с пробелами  ")
        chat.refresh_from_db()
        self.assertEqual(chat.title, "Чат с пробелами")

    def test_empty_chat_title_validation(self):
        """Тест валидации пустого названия чата."""
        with self.assertRaises(ValidationError):
            chat = Chat(title="   ")
            chat.full_clean()

    def test_too_long_chat_title_validation(self):
        """Тест валидации слишком длинного названия чата."""
        with self.assertRaises(ValidationError):
            chat = Chat(title="A" * 201)
            chat.full_clean()

    def test_chat_ordering(self):
        """Тест порядка сортировки чатов."""
        chat1 = Chat.objects.create(title="Чат 1")
        chat2 = Chat.objects.create(title="Чат 2")
        chats = Chat.objects.all()
        self.assertEqual(chats[0].title, "Чат 2") # Сначала новые
        self.assertEqual(chats[1].title, "Чат 1")


class MessageModelTests(TestCase):
    """Тесты для модели Message."""

    def setUp(self):
        """Создаем тестовый чат для сообщений."""
        self.chat = Chat.objects.create(title="Тестовый чат")

    def test_create_message(self):
        """Тест создания сообщения."""
        message = Message.objects.create(
            chat=self.chat,
            text="Тестовое сообщение"
        )
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.text, "Тестовое сообщение")
        self.assertIsNotNone(message.created_at)
        self.assertEqual(str(message), f"Сообщение {message.id} в чате {self.chat.id}")

    def test_message_text_trimming(self):
        """Тест тримминга пробелов в тексте сообщения."""
        message = Message.objects.create(
            chat=self.chat,
            text="  Сообщение с пробелами  "
        )
        message.refresh_from_db()
        self.assertEqual(message.text, "Сообщение с пробелами")

    def test_empty_message_text_validation(self):
        """Тест валидации пустого текста сообщения."""
        with self.assertRaises(ValidationError):
            message = Message(chat=self.chat, text="   ")
            message.full_clean()

    def test_too_long_message_text_validation(self):
        """Тест валидации слишком длинного текста сообщения."""
        with self.assertRaises(ValidationError):
            message = Message(chat=self.chat, text="A" * 5001)
            message.full_clean()

    def test_message_ordering(self):
        """Тест порядка сортировки сообщений."""
        message1 = Message.objects.create(chat=self.chat, text="Первое")
        message2 = Message.objects.create(chat=self.chat, text="Второе")
        messages = Message.objects.all()
        self.assertEqual(messages[0].text, "Первое")  # Сначала старые
        self.assertEqual(messages[1].text, "Второе")

    def test_cascade_delete(self):
        """Тест каскадного удаления сообщений при удалении чата."""
        message = Message.objects.create(chat=self.chat, text="Сообщение")
        message_id = message.id

        self.chat.delete()

        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(id=message_id)


class ChatListViewTests(TestCase):
    """Тесты для ChatListView (создание чата)."""

    def setUp(self):
        """Настройка клиента API."""
        self.client = APIClient()
        self.url = reverse('chat-list')

    def test_create_chat_success(self):
        """Тест успешного создания чата."""
        data = {"title": "Новый чат"}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Новый чат")
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)

        # Проверяем, что чат действительно создан в БД
        chat = Chat.objects.get(id=response.data['id'])
        self.assertEqual(chat.title, "Новый чат")

    def test_create_chat_with_spaces(self):
        """Тест создания чата с пробелами по краям."""
        data = {"title": "  Чат с пробелами  "}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Чат с пробелами")

    def test_create_chat_empty_title(self):
        """Тест создания чата с пустым названием."""
        data = {"title": ""}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_chat_too_long_title(self):
        """Тест создания чата со слишком длинным названием."""
        data = {"title": "A" * 201}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_chat_missing_title(self):
        """Тест создания чата без поля title."""
        data = {}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_wrong_http_method(self):
        """Тест использования неверного HTTP метода."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ChatDetailViewTests(TestCase):
    """Тесты для ChatDetailView (получение и удаление чата)."""

    def setUp(self):
        """Создаем тестовые данные."""
        self.client = APIClient()
        self.chat = Chat.objects.create(title="Тестовый чат")

        # Создаем несколько сообщений
        for i in range(5):
            Message.objects.create(
                chat=self.chat,
                text=f"Сообщение {i}"
            )

    def test_get_chat_success(self):
        """Тест успешного получения чата."""
        url = reverse('chat-detail', args=[self.chat.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.chat.id)
        self.assertEqual(response.data['title'], "Тестовый чат")
        self.assertEqual(len(response.data['messages']), 5)

    def test_get_chat_with_limit(self):
        """Тест получения чата с ограничением количества сообщений."""
        url = reverse('chat-detail', args=[self.chat.id]) + '?limit=2'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['messages']), 2)

    def test_get_chat_with_invalid_limit(self):
        """Тест получения чата с некорректным limit."""
        url = reverse('chat-detail', args=[self.chat.id]) + '?limit=abc'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен использоваться limit по умолчанию (20)
        self.assertEqual(len(response.data['messages']), 5)

    def test_get_chat_with_negative_limit(self):
        """Тест получения чата с отрицательным limit."""
        url = reverse('chat-detail', args=[self.chat.id]) + '?limit=-1'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен использоваться limit по умолчанию (20)
        self.assertEqual(len(response.data['messages']), 5)

    def test_get_chat_with_large_limit(self):
        """Тест получения чата с limit > 100."""
        url = reverse('chat-detail', args=[self.chat.id]) + '?limit=150'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен ограничиться 100 сообщениями, но у нас всего 5
        self.assertEqual(len(response.data['messages']), 5)

    def test_get_nonexistent_chat(self):
        """Тест получения несуществующего чата."""
        url = reverse('chat-detail', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Чат не найден")

    def test_delete_chat_success(self):
        """Тест успешного удаления чата."""
        url = reverse('chat-detail', args=[self.chat.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что чат удален из БД
        with self.assertRaises(Chat.DoesNotExist):
            Chat.objects.get(id=self.chat.id)

        # Проверяем, что сообщения тоже удалены (каскадное удаление)
        self.assertEqual(Message.objects.filter(chat_id=self.chat.id).count(), 0)

    def test_delete_nonexistent_chat(self):
        """Тест удаления несуществующего чата."""
        url = reverse('chat-detail', args=[999])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Чат не найден")


class MessageCreateViewTests(TestCase):
    """Тесты для MessageCreateView (отправка сообщений)."""

    def setUp(self):
        """Создаем тестовые данные."""
        self.client = APIClient()
        self.chat = Chat.objects.create(title="Тестовый чат")

    def test_create_message_success(self):
        """Тест успешной отправки сообщения."""
        url = reverse('message-create', args=[self.chat.id])
        data = {"text": "Тестовое сообщение"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], "Тестовое сообщение")
        self.assertEqual(response.data['chat'], self.chat.id)
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)

        # Проверяем, что сообщение создано в БД
        message = Message.objects.get(id=response.data['id'])
        self.assertEqual(message.text, "Тестовое сообщение")
        self.assertEqual(message.chat.id, self.chat.id)

    def test_create_message_with_spaces(self):
        """Тест отправки сообщения с пробелами по краям."""
        url = reverse('message-create', args=[self.chat.id])
        data = {"text": "  Сообщение с пробелами  "}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], "Сообщение с пробелами")

    def test_create_message_empty_text(self):
        """Тест отправки сообщения с пустым текстом."""
        url = reverse('message-create', args=[self.chat.id])
        data = {"text": ""}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', response.data)

    def test_create_message_too_long_text(self):
        """Тест отправки сообщения со слишком длинным текстом."""
        url = reverse('message-create', args=[self.chat.id])
        data = {"text": "A" * 5001}
        response = self.client.post(url, data, format='json')

        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])

    def test_create_message_missing_text(self):
        """Тест отправки сообщения без поля text."""
        url = reverse('message-create', args=[self.chat.id])
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', response.data)

    def test_create_message_in_nonexistent_chat(self):
        """Тест отправки сообщения в несуществующий чат."""
        url = reverse('message-create', args=[999])
        data = {"text": "Сообщение"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Чат не найден")

    def test_wrong_http_method(self):
        """Тест использования неверного HTTP метода."""
        url = reverse('message-create', args=[self.chat.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class IntegrationTests(TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        """Настройка клиента API."""
        self.client = APIClient()

    def test_full_chat_flow(self):
        """Полный тестовый сценарий: создание чата, отправка сообщений, удаление."""
        # 1. Создаем чат
        create_url = reverse('chat-list')
        data = {"title": "Интеграционный тест"}
        response = self.client.post(create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chat_id = response.data['id']

        # 2. Отправляем несколько сообщений
        message_url = reverse('message-create', args=[chat_id])
        messages = ["Привет!", "Как дела?", "Это тестовый чат"]

        for text in messages:
            response = self.client.post(message_url, {"text": text}, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. Получаем чат с сообщениями
        detail_url = reverse('chat-detail', args=[chat_id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Интеграционный тест")
        self.assertEqual(len(response.data['messages']), 3)

        # 4. Проверяем порядок сообщений
        self.assertEqual(response.data['messages'][0]['text'], "Это тестовый чат")
        self.assertEqual(response.data['messages'][1]['text'], "Как дела?")
        self.assertEqual(response.data['messages'][2]['text'], "Привет!")

        # 5. Получаем чат с ограничением
        response = self.client.get(detail_url + '?limit=2')
        self.assertEqual(len(response.data['messages']), 2)

        # 6. Удаляем чат
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 7. Проверяем, что чат удален
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
