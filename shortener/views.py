# Django
from django.db.models import Q
from django.http import HttpResponseGone
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

# Django REST Framework
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .models import ShortURL
from .pagination import ShortURLPagination
from .permissions import IsOwner
from .serializers import ShortURLSerializer

# API modules
from .api.dashboard import DashboardView
from .api.redirect import redirect_url
from .api.analytics import AnalyticsView
from .api.my_urls import MyURLsView


class CreateShortURL(APIView):

    def post(self, request):

        serializer = ShortURLSerializer(data=request.data)

        if serializer.is_valid():

            if request.user.is_authenticated:
                url = serializer.save(owner=request.user)
            else:
                url = serializer.save()

            code = url.custom_alias or url.short_code
            short_url = request.build_absolute_uri(f"/{code}")

            url.generate_qr_code(short_url)
            url.save()

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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateShortURL(APIView):

    permission_classes = [IsAuthenticated]

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


class DeleteShortURL(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def delete(self, request, pk):

        url = get_object_or_404(
            ShortURL,
            pk=pk,
        )

        self.check_object_permissions(request, url)

        url.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    