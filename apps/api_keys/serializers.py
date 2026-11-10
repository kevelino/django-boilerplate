from rest_framework import serializers

from apps.api_keys.models import ApiKey


class ApiKeySerializer(serializers.ModelSerializer):
    raw_key = serializers.CharField(read_only=True)

    class Meta:
        model = ApiKey
        fields = ("id", "name", "prefix", "scopes", "is_active", "expires_at",
                  "last_used_at", "created_at", "raw_key")
        read_only_fields = ("id", "prefix", "is_active", "last_used_at", "created_at", "raw_key")

    def create(self, validated_data):
        user = self.context["request"].user
        instance, raw = ApiKey.create_key(
            user=user,
            name=validated_data["name"],
            scopes=validated_data.get("scopes", []),
        )
        instance.raw_key = raw  # type: ignore[attr-defined]
        return instance