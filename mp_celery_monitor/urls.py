from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import celery_check

app_name = "mp_celery_monitor"

urlpatterns = [
    path("", csrf_exempt(celery_check), name="celery_check")
]