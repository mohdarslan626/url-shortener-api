from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..models import ShortURL
from ..pagination import ShortURLPagination
from ..serializers import ShortURLSerializer


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
        return (
            ShortURL.objects
            .filter(owner=self.request.user)
            .order_by("-created_at")
        )
    