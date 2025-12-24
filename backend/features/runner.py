from django_behave.runner import *

from django.conf import settings


class PJBehaveTestCase(DjangoBehaveTestCase):
    def __init__(self, **kwargs):
        super(PJBehaveTestCase, self).__init__(**kwargs)
        if settings.DEBUG == False:
            settings.DEBUG = True


class TestSuiteRunner(DjangoBehaveTestSuiteRunner):
    def make_bdd_test_suite(self, features_dir):
        return PJBehaveTestCase(features_dir=features_dir, option_info=self.option_info)
