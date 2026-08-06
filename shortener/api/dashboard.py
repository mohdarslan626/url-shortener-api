from django.db.models import Sum, Q
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from shortener.models import ShortURL


class DashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        urls = ShortURL.objects.filter(owner=request.user)

        total_urls = urls.count()

        active_urls = urls.filter(Q(expires_at__isnull=True) | 
                                  Q(expires_at__gt=timezone.now())).count()

        expired_urls = urls.filter(
            expires_at__lt=timezone.now()
        ).count()

        total_clicks = (
            urls.aggregate(
                total=Sum("clicks")
            )["total"] or 0
        )

        most_clicked = (
            urls.order_by("-clicks")
            .first()
        )

        recent_urls = (
            urls.order_by("-created_at")[:5]
        )

        return Response(
            { 
                "summary": {
                    "total_urls": total_urls,
                    "active_urls": active_urls,
                    "expired_urls": expired_urls,
                    "total_clicks": total_clicks,
                },

                "most_clicked_url": (
                    {
                        "id": most_clicked.id,
                        "short_code": most_clicked.custom_alias
                        or most_clicked.short_code,
                        "clicks": most_clicked.clicks,
                    }
                    if most_clicked
                    else None
                ),

                "recent_urls": [
                    {
                        "id": url.id,
                        "short_code": url.custom_alias or url.short_code,
                        "original_url": url.original_url,
                        "clicks": url.clicks,
                        "created_at": url.created_at,
                    }
                    for url in recent_urls
                ],
            }
        )
    