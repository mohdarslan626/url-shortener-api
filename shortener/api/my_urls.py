from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ShortURL
from ..pagination import ShortURLPagination
from ..serializers import ShortURLSerializer
from ..services.cache import RedisCacheService
from ..services.cache_keys import my_urls_cache_key


class MyURLsView(generics.ListAPIView):

    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ShortURLPagination

    search_fields = (
        "original_url",
        "custom_alias",
        "short_code",
    )

    ordering_fields = (
        "clicks",
        "created_at",
    )

    ordering = ("-created_at",)

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return ShortURL.objects.none()

        return ShortURL.objects.filter(owner=self.request.user).order_by("-created_at")

    def list(self, request, *args, **kwargs):

        cache = RedisCacheService()

        query_string = request.META.get(
            "QUERY_STRING",
            "",
        )

        cache_key = my_urls_cache_key(
            request.user.id,
            query_string,
        )

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().list(
            request,
            *args,
            **kwargs,
        )

        cache.set(
            cache_key,
            response.data,
            timeout=300,
        )

        return response
