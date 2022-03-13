from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("BaseModel.created_at"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("BaseModel.created_by"),
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("BaseModel.updated_at")
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("BaseModel.updated_by"),
    )

    class Meta:
        abstract = True
