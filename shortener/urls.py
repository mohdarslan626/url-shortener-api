from django.urls import path
from .views import CreateShortURL, AnalyticsView, MyURLsView

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
]
