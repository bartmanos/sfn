import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.models import Goods, Needs, Poi, PoiMembership, Shipments, User

logger = logging.getLogger(__name__)

admin.site.site_title = _("Home")
admin.site.site_header = _("Home")


def _has_add_permission(request, codenames) -> bool:
    try:
        membership = request.user.member.all()[:]
        if membership:
            try:
                for codename in codenames:
                    membership[0].group.permissions.get(codename=codename)
            except Permission.DoesNotExist:
                return False
            else:
                return True
    except AttributeError:
        return False


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fields = readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None) -> bool:
        if super().has_change_permission(request, obj):
            return True
        else:
            return obj and obj.created_by == request.user

    def has_view_permission(self, request, obj=None) -> bool:
        if super().has_view_permission(request, obj):
            return True
        elif not obj:
            # editing of objects of this type is permitted in general
            return True
        else:
            return obj.created_by == request.user

    def has_module_permission(self, request) -> bool:
        if super().has_module_permission(request):
            return True
        else:
            return True

    def _only_my_pois(self, user, perms):
        pois = []
        if user.is_anonymous:
            return pois

        if user.is_superuser:
            pois.extend([poi.id for poi in Poi.objects.all()])
            return pois

        memberships = PoiMembership.objects.filter(member=user, is_active=True).all()
        for membership in memberships:
            for perm in membership.group.permissions.all():
                if perm.codename in perms:
                    logging.info("User %s allowed to %s for %s", user, perm, membership.poi)
                    pois.append(membership.poi.id)
        return pois


@admin.register(Goods)
class GoodsAdmin(BaseModelAdmin):
    fields = [
        "name",
        "description",
        "link",
        "poi",
    ] + BaseModelAdmin.fields

    search_fields = [
        "name",
        "description",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Dropdown shows only POIs in which user has active membership
        # with high enough permissions to add goods
        if db_field.name == "poi":
            pois = self._only_my_pois(request.user, ["add_goods"])
            kwargs["queryset"] = Poi.objects.filter(id__in=pois)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request) -> bool:
        if super().has_add_permission(request):
            return True
        else:
            pois = self._only_my_pois(request.user, ["add_goods"])
            return bool(pois)

    def get_queryset(self, request):
        # User should see only Membership in POI in which is admin or user
        logging.debug("User %s requesting goods list in admin", request.user)
        qs = super().get_queryset(request)
        pois = self._only_my_pois(request.user, ["view_goods", "change_goods", "add_goods"])
        return qs.filter(poi_id__in=pois)


@admin.register(Needs)
class NeedsAdmin(BaseModelAdmin):
    fields = [
        "good",
        "quantity",
        "unit",
        "due_time",
        "poi",
        "status",
        # "shipment",
    ] + BaseModelAdmin.fields

    list_display = [
        "poi",
        "good",
        "quantity",
        "unit",
        "due_time",
        "status",
        "created_by",
        "created_at",
        "updated_at",
        "share_on_facebook",
    ]

    search_fields = ["good__name", "good__description"]

    @admin.display(description=_("Share on Facebook"))
    def share_on_facebook(self, obj):
        return format_html(
            f'<a href="https://www.facebook.com/sharer/sharer.php?u=https://sfn-project.org{obj.get_absolute_url()}" '
            f'target="_blank">{_("Share on Facebook")}</a>'
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Dropdown shows only POIs in which user has active membership
        # with high enough permissions to add needs
        if db_field.name == "poi":
            pois = self._only_my_pois(request.user, ["add_needs"])
            kwargs["queryset"] = Poi.objects.filter(id__in=pois)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request) -> bool:
        if super().has_add_permission(request):
            return True
        else:
            pois = self._only_my_pois(request.user, ["add_needs"])
            return bool(pois)

    def get_queryset(self, request):
        # User should see only Membership in POI in which is admin or user
        logging.debug("User %s requesting needs list in admin", request.user)
        qs = super().get_queryset(request)
        pois = self._only_my_pois(request.user, ["view_needs", "change_needs", "add_needs"])
        return qs.filter(poi_id__in=pois)


# @admin.register(Organization)
# class OrganizationAdmin(BaseModelAdmin):
#     fields = [
#         "name",
#         "description",
#         "contact",
#     ] + BaseModelAdmin.fields
#
#     search_fields = [
#         "good__name",
#         "good__description"
#     ]


@admin.register(Poi)
class PoiAdmin(BaseModelAdmin):
    fields = [
        "name",
        "description",
        "contact",
        # "organization",
    ] + BaseModelAdmin.fields

    search_fields = ["good__name", "good__description"]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    search_fields = [
        "description",
    ]


@admin.register(PoiMembership)
class PoiMembershipAdmin(BaseModelAdmin):
    fields = [
        "member",
        "poi",
        "group",
        "is_active",
    ] + BaseModelAdmin.fields

    list_display = [
        "member",
        "poi",
        "group",
        "is_active",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Dropdown shows only POIs in which user has active membership
        # with high enough permissions to add needs
        if db_field.name == "group":
            kwargs["queryset"] = Group.objects.filter(name__in=["POI admin", "POI user"])
        if db_field.name == "poi":
            pois = self._only_my_pois(request.user, ["add_poimembership", "change_poimembership"])
            kwargs["queryset"] = Poi.objects.filter(id__in=pois)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request) -> bool:
        if super().has_add_permission(request):
            return True
        else:
            pois = self._only_my_pois(request.user, ["add_poimembership"])
            return bool(pois)

    def has_module_permission(self, request) -> bool:
        if super(BaseModelAdmin, self).has_module_permission(request):
            return True
        else:
            pois = self._only_my_pois(request.user, ["view_poimembership"])
            return bool(pois)

    def has_change_permission(self, request, obj=None) -> bool:
        # No, you cannot change membership even it was created by you,
        # hence we call super on BaseModelAdmin, not on PoiMembershipAdmin
        if super(BaseModelAdmin, self).has_change_permission(request, obj):
            return True
        else:
            if obj is None:
                return True

            # We need to see if you want to change someones membership
            # in one of POIs where you change_poimembership.
            pois = self._only_my_pois(request.user, ["change_poimembership"])
            logger.info(
                "User %s is allowed to manage membership in POIs %s and is changing in %s for %s",
                request.user,
                pois,
                obj.poi.id,
                obj.member,
            )
            return obj.poi.id in pois

    def get_queryset(self, request):
        # User should see only Membership in POI in which is admin or user
        logging.debug("User %s requesting membership list in admin", request.user)
        qs = super().get_queryset(request)
        pois = self._only_my_pois(request.user, ["view_poimembership"])
        return qs.filter(poi_id__in=pois)


@admin.register(Shipments)
class ShipmentsAdmin(BaseModelAdmin):
    fields = [
        "need",
        "status",
        "created_by",
    ] + BaseModelAdmin.fields

    list_display = [
        "poi_name",
        "need_name",
        "need_quantity",
        "status",
        "created_by",
        "created_at",
        "updated_at",
    ]

    @admin.display(description=_("Goods.name"))
    def need_name(self, obj):
        return obj.need.good.name

    @admin.display(description=_("Needs.quantity"))
    def need_quantity(self, obj):
        return f"{obj.need.quantity}{obj.need.get_unit_display()}"

    @admin.display(description=_("Poi.name"))
    def poi_name(self, obj):
        return obj.need.poi.name

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # I.e. user without change permission
        if not form.base_fields:
            return form

        form.base_fields["need"].queryset = Needs.objects.filter(status=Needs.Status.ACTIVE)
        if obj is None:
            form.base_fields["created_by"].initial = request.user.pk
        form.base_fields["created_by"].disabled = True
        return form

    def has_add_permission(self, request) -> bool:
        if super().has_add_permission(request):
            return True
        else:
            return _has_add_permission(request, ["add_shipments"])

    def has_change_permission(self, request, obj=None) -> bool:
        # No, you cannot change shipment even it was created by you,
        # hence we call super on BaseModelAdmin, not on ShipmentsModel
        if super(BaseModelAdmin, self).has_change_permission(request, obj):
            return True
        else:
            return False

    def get_queryset(self, request):
        # User should see only Shipments to POI in which is admin or user
        logging.debug("User %s requesting list of shipments in admin", request.user)
        qs = super().get_queryset(request)
        memberships = PoiMembership.objects.filter(member=request.user, is_active=True).all()
        pois = []
        for membership in memberships:
            for perm in membership.group.permissions.all():
                if perm.codename == "view_shipments":
                    logging.info("User %s allowed to view shipments for %s", request.user, membership.poi)
                    pois.append(membership.poi.id)

        return qs.filter(need__poi_id__in=pois)
