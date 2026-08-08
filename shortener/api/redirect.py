from django.db.models import Q
from django.http import HttpResponseGone
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from ..models import ShortURL


def redirect_url(request, code):

    url = get_object_or_404(
        ShortURL,
        Q(short_code=code) | Q(custom_alias=code),
    )

    if not url.is_active:
        return HttpResponseGone(
            "This URL has been disabled."
        )

    if url.expires_at and url.expires_at <= timezone.now():
        return HttpResponseGone(
            "This URL has expired."
        )

    url.clicks += 1
    url.save(update_fields=["clicks"])

    return redirect(url.original_url)
