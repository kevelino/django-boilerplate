from django.contrib import admin

from apps.api_keys.models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "prefix", "is_active", "expires_at", "last_used_at", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "user__email", "prefix")
    readonly_fields = ("prefix", "hashed_key", "last_used_at", "created_at", "updated_at")