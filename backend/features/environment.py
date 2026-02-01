import django
import os
from splinter.browser import Browser
from peeldb.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobsp.settings_server")

django.setup()


def before_all(context):
    User.objects.filter(email="test@mp.com").delete()
    context.browser = Browser("firefox")
    context.server_url = "http://test.peeljobs.com:8000"


def after_all(context):
    context.browser.quit()
    context.browser = None
