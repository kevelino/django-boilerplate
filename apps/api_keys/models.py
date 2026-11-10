import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.utils.models import BaseModel


def _generate_token() -> str:
    return "sk_" + secrets.token_urlsafe(32)


class ApiKey(BaseModel):
    """A personal API key belonging to a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=12, db_index=True)
    hashed_key = models.CharField(max_length=128)
    scopes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "API key"
        verbose_name_plural = "API keys"

    def __str__(self) -> str:
        return f"{self.name} ({self.prefix}...)"

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at <= timezone.now())

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired

    @classmethod
    def create_key(cls, user, name, scopes=None, expires_in_days=None):
        """Create a new API key, returning (instance, raw_key). The raw key is
        only available at creation time and is never stored in plain text."""
        raw = _generate_token()
        prefix = raw[:12]
        hashed = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        instance = cls.objects.create(
            user=user,
            name=name,
            prefix=prefix,
            hashed_key=hashed,
            scopes=scopes or [],
            expires_at=expires_at,
        )
        return instance, raw

    def check_key(self, raw: str) -> bool:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest() == self.hashed_key

    def mark_used(self):
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])