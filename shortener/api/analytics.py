from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ShortURL


class AnalyticsView(APIView):

    @extend_schema(
    responses={200: dict},
    )
    def get(self, request, code):

        url = get_object_or_404(
            ShortURL,
            Q(short_code=code) | Q(custom_alias=code),
        )

        return Response(
            {
                "original_url": url.original_url,
                "short_code": url.short_code,
                "custom_alias": url.custom_alias,
                "clicks": url.clicks,
                "is_active": url.is_active,
                "expires_at": url.expires_at,
                "created_at": url.created_at,
                "updated_at": url.updated_at,
            }
        )
    