from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
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


class PoiMembership(BaseModel):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="member", on_delete=models.PROTECT)
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.poi.name}: {self.member.first_name} {self.member.last_name} ({self.group.name})"


class Goods(BaseModel):
    name = models.TextField(_("Goods.name"))
    description = models.TextField(_("Goods.description"), blank=True)
    link = models.TextField(_("Goods.link"), blank=True)
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Goods")
        verbose_name_plural = _("Goods")

    def __str__(self):
        return self.name


class Needs(BaseModel):
    class Units(models.TextChoices):
        KG = _("Needs.Units.kg")
        L = _("Needs.Units.l")
        PCS = _("Needs.Units.pcs")

    class Status(models.TextChoices):
        ACTIVE = _("Needs.Status.active")
        DISABLED = _("Needs.Status.disabled")
        FULFILLED = _("Needs.Status.fulfilled")

    good = models.ForeignKey(Goods, on_delete=models.PROTECT, verbose_name=_("Needs.good"))
    quantity = models.DecimalField(_("Needs.quantity"), max_digits=10, decimal_places=2)
    unit = models.CharField(_("Needs.unit"), choices=Units.choices, max_length=16)
    due_time = models.DateTimeField(_("Needs.due_time"))
    poi = models.ForeignKey(Poi, on_delete=models.PROTECT, verbose_name=_("Needs.poi"))
    status = models.CharField(_("Needs.status"), choices=Status.choices, default=Status.ACTIVE, max_length=32)

    class Meta:
        verbose_name = _("Needs")
        verbose_name_plural = _("Needs")

    def __str__(self):
        return f"{self.good.name} - {self.quantity} {self.unit} - {_('Needs.due_time')}: {self.due_time}"


class Shipments(BaseModel):
    class Status(models.TextChoices):
        TO_DO = _("Shipments.Status.to_do")
        IN_PROGRESS = _("Shipments.Status.in_progress")
        DONE = _("Shipments.Status.done")

    need = models.ForeignKey(Needs, on_delete=models.PROTECT, verbose_name=_("Shipments.need"))
    status = models.CharField(_("Shipments.status"), choices=Status.choices, max_length=32)

    def save(self, *args, **kwargs):
        self.need.status = Needs.Status.FULFILLED if self.status == self.Status.DONE else Needs.Status.DISABLED
        self.need.save()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Shipments")
        verbose_name_plural = _("Shipments")

    def __str__(self):
        return f"{self.need} - {self.status}"
