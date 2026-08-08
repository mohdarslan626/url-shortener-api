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
from .api.create import CreateShortURL
from .api.update import UpdateShortURL


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
    
    