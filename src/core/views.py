from django.views.generic import ListView
from core.models import Needs


class NeedsView(ListView):
    model = Needs
