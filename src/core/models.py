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

    class Meta:
        abstract = True


class Organization(BaseModel):
    name = models.TextField(_("Organization.name"))
    description = models.TextField(_("Organization.description"))
    contact = models.TextField(_("Organization.contact"))


class Poi(BaseModel):
    name = models.TextField(_("Poi.name"))
    description = models.TextField(_("Poi.description"))
    contact = models.TextField(_("Poi.contact"))
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, verbose_name=_("Poi.organization")
    )


class Goods(BaseModel):
    name = models.TextField(_("Goods.name"))
    description = models.TextField(_("Goods.description"), blank=True)
    link = models.TextField(_("Goods.link"), blank=True)


class Needs(BaseModel):
    class Units(models.TextChoices):
        KG = _("Needs.Units.kg")
        L = _("Needs.Units.l")
        PCS = _("Needs.Units.pcs")

    class Status(models.TextChoices):
        ACTIVE = _("Needs.Status.active")
        DISABLED = _("Needs.Status.disabled")

    good = models.ForeignKey(
        Goods, on_delete=models.PROTECT, verbose_name=_("Needs.good")
    )
    quantity = models.DecimalField(_("Needs.quantity"), max_digits=10, decimal_places=2)
    unit = models.CharField(_("Needs.unit"), choices=Units.choices, max_length=16)
    due_time = models.DateTimeField(_("Needs.due_time"))
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT, verbose_name=_("Needs.poi"))
    status = models.CharField(_("Needs.status"), choices=Status.choices, max_length=32)
