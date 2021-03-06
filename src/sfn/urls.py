"""sfn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from core.views import (
    MyShipmentsView,
    NeedView,
    PoiView,
    need_endpoint,
    poi_needs_fb_sharer_img,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("terms/", TemplateView.as_view(template_name="terms.html")),
    path("privacy/", TemplateView.as_view(template_name="privacy.html")),
    path("moje-dostawy/", MyShipmentsView.as_view(), name="my-shipments"),
    path("potrzeba/<int:pk>", NeedView.as_view(), name="need"),
    path("poi/<int:pk>/", PoiView.as_view(), name="poi-detail"),
    path("poi/<int:pk>/potrzeby/img", poi_needs_fb_sharer_img, name="poi-needs-img"),
    path("", need_endpoint, name="needs"),
]
