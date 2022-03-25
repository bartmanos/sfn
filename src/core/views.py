import datetime

from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from core.img import FbSharerImg
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

    def get_context_data(self, **kwargs):
        kwargs["needs"] = kwargs["object"].needs_set.filter(status=Needs.Status.ACTIVE)
        return kwargs


class NeedView(DetailView):
    model = Needs


def poi_needs_fb_sharer_img(request, pk: int):
    poi = Poi.objects.get(pk=pk)
    needs = Needs.objects.filter(poi_id=pk, status=Needs.Status.ACTIVE)
    text = f"{poi.name} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} potrzebujemy:\n\n"
    text += "\n".join(["- " + need.good.name for need in needs])
    text += "\n"
    fb = FbSharerImg()
    img = fb.create(text)
    response = HttpResponse(headers={"Content-Type": "image/png"})
    img.save(response, "PNG")
    return response
