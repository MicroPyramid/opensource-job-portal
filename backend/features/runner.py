from django.conf import settings
from django_behave.runner import *


class PJBehaveTestCase(DjangoBehaveTestCase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not settings.DEBUG:
            settings.DEBUG = True


class TestSuiteRunner(DjangoBehaveTestSuiteRunner):
    def make_bdd_test_suite(self, features_dir):
        return PJBehaveTestCase(features_dir=features_dir, option_info=self.option_info)
