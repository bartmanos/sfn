from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from core.models import Needs, Poi, Shipments


def need_endpoint(request):
    context = {"needs": Needs.objects.filter(status=Needs.Status.ACTIVE).order_by("-created_at")}
    if request.method == "POST":
        try:
            need_id = request.GET.get("need_id")
            Shipments.objects.create(
                need_id=need_id,
                status=Shipments.Status.IN_PROGRESS,
                created_by=request.user,
            )
        except ValidationError as e:
            context["errors"] = dict(e).values()

    return render(
        request=request,
        template_name="core/needs_list.html",
        context=context,
    )


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


class PoiView(DetailView):
    model = Poi
