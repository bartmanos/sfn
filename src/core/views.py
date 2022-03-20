from django.http import HttpResponseForbidden
from django.views.generic import ListView

from core.models import Needs, Shipments


class NeedsView(ListView):
    queryset = Needs.objects.filter(status=Needs.Status.ACTIVE).order_by("-created_at")


class MyShipmentsView(ListView):
    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise HttpResponseForbidden

        unrealized = (
            Shipments.objects.filter(created_by=self.request.user)
            .exclude(status=Shipments.Status.DONE)
            .order_by("-created_at")
        )
        realized = Shipments.objects.filter(created_by=self.request.user, status=Shipments.Status.DONE).order_by(
            "-created_at"
        )
        return realized.union(unrealized)
