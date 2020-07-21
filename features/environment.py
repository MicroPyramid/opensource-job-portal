import django
import os
from django.core.management import call_command
from splinter.browser import Browser
from features.helpers import initiate_test_data
from peeldb.models import User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobsp.settings_local")

django.setup()


def before_all(context):
    User.objects.filter(email="test@mp.com").delete()
    context.browser = Browser("firefox")
    context.server_url = "http://test.peeljobs.com:8000"


def after_all(context):
    context.browser.quit()
    context.browser = None
