from django.conf import settings
from datetime import datetime, timedelta
from django.core import management
from django.contrib.contenttypes.models import ContentType
from peeldb.models import Skill, City, State, Country


def initiate_test_data():
    country = Country.objects.create(name="India")
    state = State.objects.create(name="Telangana", country_id=country.id)
    City.objects.create(name="hyderabad", state_id=state.id)
    Skill.objects.create(name="Python", slug="python", status="Active")
    Skill.objects.create(name="PHP", slug="php", status="Active")
