from django.urls import path
from .views import CreateShortURL, AnalyticsView, MyURLsView, UpdateShortURL, DeleteShortURL

urlpatterns = [
    path(
        "shorten/",
        CreateShortURL.as_view(),
        name="shorten-url"
    ),

    path(
        "analytics/<str:code>/",
        AnalyticsView.as_view(),
        name="analytics"
    ),

    path(
    "my-urls/",
    MyURLsView.as_view(),
    name="my-urls",
    ),

    path(
    "urls/<int:pk>/",
    UpdateShortURL.as_view(),
    name="update-url",
    ),

    path(
    "urls/<int:pk>/delete/",
    DeleteShortURL.as_view(),
    name="delete-url",
    ),
]
