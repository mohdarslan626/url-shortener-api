import logging
from django.db.models import Q
from django.http import HttpResponseGone
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from ..models import ShortURL

logger = logging.getLogger(__name__)


@extend_schema(
    responses={302: None},
)
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

    logger.info(
        "Short URL redirected successfully: url_id=%s, short_code=%s",
        url.id,
        code,
    )

    return redirect(url.original_url)
