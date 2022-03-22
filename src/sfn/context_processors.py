from django.conf import settings as app_settings


def settings(request):
    return {
        "DEMO": app_settings.DEMO,
    }


def fb_share(request):
    return {
        "og_url": request.build_absolute_uri().split("?")[0],
    }
