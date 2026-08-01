from django.db.models import Q
from django.http import HttpResponse, HttpResponseGone
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import ShortURL
from .serializers import ShortURLSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner

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


def redirect_url(request, code):

    url = get_object_or_404(
        ShortURL,
        Q(short_code=code) | Q(custom_alias=code),
    )

    if not url.is_active:
        return HttpResponseGone("This URL has been disabled.")

    if url.expires_at and url.expires_at <= timezone.now():
        return HttpResponseGone("This URL has expired.")

    url.clicks += 1
    url.save(update_fields=["clicks"])

    return redirect(url.original_url)


class AnalyticsView(APIView):

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
 
class MyURLsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        urls = ShortURL.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        serializer = ShortURLSerializer(
            urls,
            many=True,
        )

        return Response(serializer.data)


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

        self.check_object_permissions(
            request,
            url,
        )

        url.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    