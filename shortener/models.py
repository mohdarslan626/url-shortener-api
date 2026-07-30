from django.db import models
import string
import random

from django.core.files import File
from io import BytesIO
import qrcode


def generate_code(length=6):
    chars = string.ascii_letters + string.digits

    while True:
        code = "".join(random.choices(chars, k=length))

        if not ShortURL.objects.filter(short_code=code).exists():
            return code


class ShortURL(models.Model):
    original_url = models.URLField()

    short_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_code,
        db_index=True,
    )

    custom_alias = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    qr_code = models.ImageField(
    upload_to="qr_codes/",
    blank=True,
    null=True,
    )

    clicks = models.PositiveBigIntegerField(default=0)

    expires_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.custom_alias or self.short_code
    
    def generate_qr_code(self, url):

        qr = qrcode.make(url)

        buffer = BytesIO()

        qr.save(buffer, format="PNG")

        filename = f"{self.custom_alias or self.short_code}.png"

        self.qr_code.save(
            filename,
            File(buffer),
            save=False,
        )
        