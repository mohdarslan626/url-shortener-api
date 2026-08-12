from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from ..models import ShortURL
from ..permissions import IsOwner


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

        url.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    