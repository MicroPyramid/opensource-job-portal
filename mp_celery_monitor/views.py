from django.http.response import HttpResponse
from django.conf import settings

from jobsp.celery import app


def celery_check(request):
    project_key = settings.MP_CELERY_MONITOR_KEY

    if project_key == request.POST.get("project_key"):
        i = app.control.inspect()
        status = i.ping()
        if status == None:
            celery_status = "down"
        else:
            celery_status = "up"
        return HttpResponse(celery_status)
    else:
        return HttpResponse("Invalid key", status=400)
