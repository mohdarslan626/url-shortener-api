from rest_framework import serializers
from .models import ShortURL

RESERVED_ALIASES = {
    "admin",
    "api",
    "analytics",
    "docs",
    "swagger",
    "redoc",
}


class ShortURLSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShortURL
        fields = (
            "id",
            "original_url",
            "short_code",
            "custom_alias",
            "expires_at",
            "clicks",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "short_code",
            "clicks",
            "created_at",
            "updated_at",
        )

    def validate_custom_alias(self, value):
        if not value:
            return value

        value = value.strip().lower()

        if value in RESERVED_ALIASES:
            raise serializers.ValidationError(
                "This alias is reserved."
            )

        if ShortURL.objects.filter(custom_alias=value).exists():
            raise serializers.ValidationError(
                "Alias already exists."
            )

        return value

    def validate(self, attrs):
        expires_at = attrs.get("expires_at")

        if expires_at:
            from django.utils import timezone

            if expires_at <= timezone.now():
                raise serializers.ValidationError(
                    {
                        "expires_at": "Expiry date must be in the future."
                    }
                )

        return attrs
    