from django.contrib import admin
from .models import (
    Goods,
    Needs,
    Organization,
    Poi,
)


class GoodsAdmin(admin.ModelAdmin):
    pass


class NeedsAdmin(admin.ModelAdmin):
    pass


class OrganizationAdmin(admin.ModelAdmin):
    pass


class PoiAdmin(admin.ModelAdmin):
    pass


admin.site.register(Goods, GoodsAdmin)
admin.site.register(Needs, NeedsAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Poi, PoiAdmin)
