from rest_framework import authentication, exceptions

from apps.api_keys.models import ApiKey


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using an ``X-API-Key`` header."""

    keyword = "X-API-Key"

    def authenticate(self, request):
        raw = request.META.get("HTTP_X_API_KEY") or request.headers.get("X-API-Key")
        if not raw:
            return None
        try:
            prefix = raw[:12]
            candidates = ApiKey.objects.filter(prefix=prefix, is_active=True).select_related("user")
        except Exception:
            return None
        for key in candidates:
            if key.check_key(raw) and key.is_valid:
                key.mark_used()
                return key.user, key
        raise exceptions.AuthenticationFailed("Invalid or expired API key.")

    def authenticate_header(self, request):
        return self.keyword