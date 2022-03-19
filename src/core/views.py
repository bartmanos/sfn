from django.views.generic import ListView
from core.models import Needs


class NeedsView(ListView):
    queryset = Needs.objects.filter(status=Needs.Status.ACTIVE).order_by('-created_at')
