from django.db.models import Q
from django.http import HttpResponse, HttpResponseGone
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ShortURL
from .serializers import ShortURLSerializer


class CreateShortURL(APIView):

    def post(self, request):

        serializer = ShortURLSerializer(data=request.data)

        if serializer.is_valid():

            url = serializer.save()

            code = url.custom_alias or url.short_code

            return Response(
                {
                    "message": "URL shortened successfully",
                    "short_code": code,
                    "short_url": request.build_absolute_uri(f"/{code}"),
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
    