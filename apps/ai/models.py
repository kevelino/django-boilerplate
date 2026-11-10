from django.conf import settings
from django.db import models

from apps.utils.models import BaseModel


class Conversation(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=100, default="gpt-4o-mini")
    provider = models.CharField(max_length=50, default="openai")

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title or f"Conversation {self.pk}"


class Message(BaseModel):
    ROLE_CHOICES = [("user", "User"), ("assistant", "Assistant"), ("system", "System")]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens = models.IntegerField(default=0)

    class Meta:
        ordering = ["created_at"]