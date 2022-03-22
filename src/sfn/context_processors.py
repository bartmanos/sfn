from django.conf import settings as app_settings


def settings(request):
    return {
        "DEMO": app_settings.DEMO,
    }
