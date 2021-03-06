from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
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
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("BaseModel.updated_at"))

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **other_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)

        group = Group.objects.get(name="Regular user")
        group.user_set.add(user)
        return user

    def create_superuser(self, username, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    description = models.TextField(_("User.description"), blank=True)
    contact = models.TextField(_("User.contact"))

    objects = UserManager()


class Organization(BaseModel):
    name = models.TextField(_("Organization.name"))
    description = models.TextField(_("Organization.description"))
    contact = models.TextField(_("Organization.contact"))

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name


class Poi(BaseModel):
    name = models.TextField(_("Poi.name"))
    description = models.TextField(_("Poi.description"))
    contact = models.TextField(_("Poi.contact"))
    # organization = models.ForeignKey(
    #     Organization, on_delete=models.PROTECT, verbose_name=_("Poi.organization")
    # )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="members",
        through="PoiMembership",
        through_fields=("poi", "member"),
    )

    class Meta:
        verbose_name = _("Poi")
        verbose_name_plural = _("Pois")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("poi-detail", kwargs={"pk": self.pk})


class PoiMembership(BaseModel):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="member", on_delete=models.PROTECT, verbose_name=_("Member")
    )
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT, verbose_name=_("Poi.name"))
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name=_("Group.name"))
    is_active = models.BooleanField(_("PoiMembership.is_active"), default=True)

    class Meta:
        verbose_name = _("Poi.member")
        verbose_name_plural = _("Poi.members")

    def __str__(self):
        return f"{self.poi.name}: {self.member.first_name} {self.member.last_name} ({self.group.name})"


class Goods(BaseModel):
    name = models.TextField(_("Goods.name"))
    description = models.TextField(_("Goods.description"), blank=True)
    link = models.TextField(_("Goods.link"), blank=True)
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT, verbose_name=_("Poi.name"))

    class Meta:
        verbose_name = _("Good")
        verbose_name_plural = _("Goods")

    def __str__(self):
        return self.name


class Needs(BaseModel):
    class Units(models.TextChoices):
        KG = "kg", _("Needs.Units.kg")
        L = "l", _("Needs.Units.l")
        PCS = "pcs", _("Needs.Units.pcs")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Needs.Status.active")
        DISABLED = "disabled", _("Needs.Status.disabled")
        FULFILLED = "fulfilled", _("Needs.Status.fulfilled")

    good = models.ForeignKey(Goods, on_delete=models.PROTECT, verbose_name=_("Needs.good"))
    quantity = models.DecimalField(_("Needs.quantity"), max_digits=10, decimal_places=2)
    unit = models.CharField(_("Needs.unit"), choices=Units.choices, max_length=16)
    due_time = models.DateTimeField(_("Needs.due_time"))
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT, verbose_name=_("Needs.poi"))
    status = models.CharField(_("Needs.status"), choices=Status.choices, default=Status.ACTIVE, max_length=32)

    class Meta:
        verbose_name = _("Need")
        verbose_name_plural = _("Needs")

    def __str__(self):
        return (
            f"{self.good.name} - {self.quantity}{self.get_unit_display()} "
            f"- {_('Needs.due_time')}: {self.due_time} ({_(self.get_status_display())})"
        )

    def get_quantity_display(self):
        return round(self.quantity, 0)

    def get_absolute_url(self):
        return reverse("need", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.status == Needs.Status.FULFILLED:
            self.shipments_set.update(status=Shipments.Status.DONE)
        return super().save(*args, **kwargs)


class Shipments(BaseModel):
    class Status(models.TextChoices):
        TO_DO = "to do", _("Shipments.Status.to_do")
        IN_PROGRESS = "in progress", _("Shipments.Status.in_progress")
        DONE = "done", _("Shipments.Status.done")

    need = models.ForeignKey(Needs, on_delete=models.PROTECT, verbose_name=_("Shipments.need"))
    status = models.CharField(_("Shipments.status"), choices=Status.choices, max_length=32)

    def save(self, *args, **kwargs):
        self.full_clean()
        self.need.status = Needs.Status.DISABLED
        self.need.save()
        return super().save(*args, **kwargs)

    def clean(self):
        if (
            Shipments.objects.filter(
                status__in=(Shipments.Status.TO_DO, Shipments.Status.IN_PROGRESS),
                created_by=self.created_by,
            ).count()
            >= settings.SHIPMENTS_IN_PROGRESS_LIMIT
        ):
            raise ValidationError(_("Too many shipments for one user"))

    class Meta:
        verbose_name = _("Shipment")
        verbose_name_plural = _("Shipments")

    def __str__(self):
        return f"{self.need} - {self.status}"
