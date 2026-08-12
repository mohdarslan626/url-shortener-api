from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from ..models import ShortURL
from ..permissions import IsOwner
from ..serializers import ShortURLSerializer


class UpdateShortURL(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=ShortURLSerializer,
        responses={200: ShortURLSerializer},
    )
    def patch(self, request, pk):

        url = get_object_or_404(
            ShortURL,
            pk=pk,
        )

        self.check_object_permissions(request, url)

        serializer = ShortURLSerializer(
            url,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    def get_permissions(self):

        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsOwner()]

        return super().get_permissions()
    