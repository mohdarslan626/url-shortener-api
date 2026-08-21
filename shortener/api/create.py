from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
from ..serializers import ShortURLSerializer
from drf_spectacular.utils import extend_schema
from ..services.cache import RedisCacheService
from ..services.cache_keys import my_urls_cache_pattern

logger = logging.getLogger(__name__)


class CreateShortURL(APIView):

    @extend_schema(
        request=ShortURLSerializer,
        responses={
            201: ShortURLSerializer,
        },
    )
    def post(self, request):

        serializer = ShortURLSerializer(data=request.data)

        if serializer.is_valid():

            if request.user.is_authenticated:
                url = serializer.save(owner=request.user)

                cache = RedisCacheService()

                cache.delete_pattern(my_urls_cache_pattern(request.user.id))

            else:
                url = serializer.save()

            code = url.custom_alias or url.short_code
            short_url = request.build_absolute_uri(f"/{code}")

            url.generate_qr_code(short_url)
            url.save()

            logger.info(
                "Short URL created successfully: user_id=%s, short_code=%s",
                request.user.id if request.user.is_authenticated else None,
                code,
            )

            return Response(
                {
                    "message": "URL shortened successfully",
                    "short_code": code,
                    "short_url": short_url,
                    "qr_code": (
                        request.build_absolute_uri(url.qr_code.url)
                        if url.qr_code
                        else None
                    ),
                    "data": ShortURLSerializer(url).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
