from django.db import models
from django.core.exceptions import ValidationError


class Chat(models.Model):
    """Модель чата."""
    title = models.CharField(
        max_length=200,
        verbose_name="Название чата",
        help_text="Название чата (1-200 символов)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        db_table = 'chat'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (ID: {self.id})"

    def clean(self):
        """Валидация модели."""
        # Убираем пробелы по краям
        if self.title:
            self.title = self.title.strip()

        # Проверяем, что title не пустой после тримминга
        if not self.title:
            raise ValidationError("Название чата не может быть пустым.")

        # Проверяем длину
        if len(self.title) < 1 or len(self.title) > 200:
            raise ValidationError("Название чата должно содержать от 1 до 200 символов.")

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова clean()."""
        self.full_clean()
        super().save(*args, **kwargs)


class Message(models.Model):
    """Модель сообщения."""
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Чат"
    )
    text = models.TextField(
        verbose_name="Текст сообщения",
        help_text="Текст сообщения (1-5000 символов)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        db_table = 'message'
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение {self.id} в чате {self.chat_id}"

    def clean(self):
        """Валидация модели."""
        # Убираем пробелы по краям
        if self.text:
            self.text = self.text.strip()

        # Проверяем, что text не пустой после тримминга
        if not self.text:
            raise ValidationError("Текст сообщения не может быть пустым.")

        # Проверяем длину
        if len(self.text) < 1 or len(self.text) > 5000:
            raise ValidationError("Текст сообщения должен содержать от 1 до 5000 символов.")

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова clean()."""
        self.full_clean()
        super().save(*args, **kwargs)