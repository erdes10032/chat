from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, ChatDetailSerializer

logger = logging.getLogger(__name__)


class ChatListView(APIView):
    """
    API endpoint для создания нового чата.
    POST /chats/ - создать чат
    """

    @swagger_auto_schema(
        operation_description="Создание нового чата",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title'],
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Название чата (1-200 символов)',
                    maxLength=200
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Чат успешно создан",
                schema=ChatSerializer
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            )
        }
    )
    def post(self, request):
        """Создание нового чата."""
        try:
            serializer = ChatSerializer(data=request.data)

            if not serializer.is_valid():
                logger.error(f"Ошибка валидации при создании чата: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            chat = serializer.save()
            logger.info(f"Создан новый чат: {chat.id} - {chat.title}")

            return Response(
                ChatSerializer(chat).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании чата: {e}")
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatDetailView(APIView):
    """
    API endpoint для работы с конкретным чатом.
    GET /chats/{id}/ - получить чат с сообщениями
    DELETE /chats/{id}/ - удалить чат
    """

    @swagger_auto_schema(
        operation_description="Получение чата с последними сообщениями",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Количество последних сообщений (по умолчанию 20, максимум 100)",
                type=openapi.TYPE_INTEGER,
                default=20,
                minimum=1,
                maximum=100
            )
        ],
        responses={
            200: openapi.Response(
                description="Чат найден",
                schema=ChatDetailSerializer
            ),
            404: openapi.Response(
                description="Чат не найден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def get(self, request, id):
        """Получение чата с последними сообщениями."""
        try:
            # Получаем чат
            chat = Chat.objects.get(id=id)

            # Получаем параметр limit
            limit = request.query_params.get('limit', 20)
            try:
                limit = int(limit)
                if limit < 1:
                    limit = 20
                elif limit > 100:
                    limit = 100
            except ValueError:
                limit = 20

            # Получаем последние сообщения
            messages = chat.messages.order_by('-created_at')[:limit]

            # Подготавливаем данные
            chat_data = ChatSerializer(chat).data
            chat_data['messages'] = MessageSerializer(
                messages,
                many=True
            ).data

            logger.info(f"Получен чат {id} с {len(messages)} сообщениями")

            return Response(chat_data)

        except Chat.DoesNotExist:
            logger.warning(f"Попытка получить несуществующий чат: {id}")
            return Response(
                {"detail": "Чат не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Ошибка при получении чата {id}: {e}")
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Удаление чата со всеми сообщениями",
        responses={
            204: openapi.Response(
                description="Чат успешно удален"
            ),
            404: openapi.Response(
                description="Чат не найден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def delete(self, request, id):
        """Удаление чата со всеми сообщениями."""
        try:
            chat = Chat.objects.get(id=id)

            with transaction.atomic():
                chat.delete()

            logger.info(f"Удален чат: {id}")

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Chat.DoesNotExist:
            logger.warning(f"Попытка удалить несуществующий чат: {id}")
            return Response(
                {"detail": "Чат не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Ошибка при удалении чата {id}: {e}")
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessageCreateView(APIView):
    """
    API endpoint для отправки сообщения в чат.
    POST /chats/{id}/messages/ - отправить сообщение
    """

    @swagger_auto_schema(
        operation_description="Отправка сообщения в чат",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Текст сообщения (1-5000 символов)',
                    maxLength=5000
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Сообщение успешно отправлено",
                schema=MessageSerializer
            ),
            400: openapi.Response(
                description="Ошибка валидации",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'text': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="Чат не найден",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request, id):
        """Отправка сообщения в чат."""
        try:
            # Проверяем существование чата
            chat = Chat.objects.get(id=id)

            # Подготавливаем данные для сериализатора
            data = request.data.copy()
            data['chat'] = chat.id

            serializer = MessageSerializer(data=data)

            if not serializer.is_valid():
                logger.error(f"Ошибка валидации при отправке сообщения в чат {id}: {serializer.errors}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            message = serializer.save()
            logger.info(f"Отправлено сообщение {message.id} в чат {id}")

            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )

        except Chat.DoesNotExist:
            logger.warning(f"Попытка отправить сообщение в несуществующий чат: {id}")
            return Response(
                {"detail": "Чат не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке сообщения в чат {id}: {e}")
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )