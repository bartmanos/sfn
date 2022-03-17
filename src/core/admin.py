from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import (
    Goods,
    Needs,
    Organization,
    Poi,
    PoiMembership,
    User,
)


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


@admin.register(Goods)
class GoodsAdmin(BaseModelAdmin):
    fields = [
        "name",
        "description",
        "link"
    ] + BaseModelAdmin.fields

    search_fields = [
        "name",
        "description",
    ]

    def has_add_permission(self, request) -> bool:
        membership = request.user.member.all()[:]
        print(membership)
        if membership:
            permissions = membership[0].group.permissions.all()
            print(permissions)

        print('===')
        return True

    # def has_change_permission(self, request, obj=None) -> bool:
    #     if super().has_change_permission(request, obj):
    #         return True
    #     elif not obj:
    #         return True
    #     else:
    #         return obj.created_by == request.user


@admin.register(Needs)
class NeedsAdmin(BaseModelAdmin):
    fields = [
        "good",
        "quantity",
        "unit",
        "due_time",
        "poi",
        "status",
    ] + BaseModelAdmin.fields

    search_fields = [
        "good__name",
        "good__description"
    ]


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

    search_fields = [
        "good__name",
        "good__description"
    ]


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
