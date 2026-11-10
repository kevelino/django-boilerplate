from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api_keys.models import ApiKey
from apps.api_keys.serializers import ApiKeySerializer


class ApiKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        raw = getattr(instance, "raw_key", None)
        headers = self.get_success_headers(serializer.data)
        data = ApiKeySerializer(instance).data
        if raw:
            data["raw_key"] = raw
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        key = self.get_object()
        key.is_active = False
        key.save(update_fields=["is_active", "updated_at"])
        return Response({"status": "revoked"})