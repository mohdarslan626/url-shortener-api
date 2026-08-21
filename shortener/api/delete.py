import logging
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from ..models import ShortURL
from ..permissions import IsOwner
from ..services.cache import RedisCacheService
from ..services.cache_keys import my_urls_cache_pattern

logger = logging.getLogger(__name__)


class DeleteShortURL(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    @extend_schema(
        responses={204: None},
    )
    def delete(self, request, pk):

        url = get_object_or_404(
            ShortURL,
            pk=pk,
        )

        self.check_object_permissions(
            request,
            url,
        )

        owner_id = url.owner_id
        url.delete()

        cache = RedisCacheService()
        cache.delete_pattern(my_urls_cache_pattern(owner_id))

        logger.info(
            "Short URL deleted successfully: user_id=%s, url_id=%s",
            request.user.id,
            pk,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
