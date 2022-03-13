from django.contrib import admin
from core.models import (
    Goods,
    Needs,
    Organization,
    Poi,
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


@admin.register(Goods)
class GoodsAdmin(BaseModelAdmin):
    fields = [
        "name",
        "description",
        "link"
    ] + BaseModelAdmin.fields


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


@admin.register(Organization)
class OrganizationAdmin(BaseModelAdmin):
    fields = [
        "name",
        "description",
        "contact",
    ] + BaseModelAdmin.fields


@admin.register(Poi)
class PoiAdmin(BaseModelAdmin):
    fields = [
        "name",
        "description",
        "contact",
        "organization",
    ] + BaseModelAdmin.fields
