from django.core.management.base import BaseCommand
from django.core.management import call_command
import json


class Command(BaseCommand):
    args = '<filename>'
    help = 'Loads the initial data in to database'

    def handle(self, *args, **options):

        call_command('loaddata', 'peeldb/fixtures/countries.json', verbosity=0)
        call_command('loaddata', 'peeldb/fixtures/states.json', verbosity=0)
        call_command('loaddata', 'peeldb/fixtures/cities.json', verbosity=0)
        call_command('loaddata', 'peeldb/fixtures/skills.json', verbosity=0)
        call_command('loaddata', 'peeldb/fixtures/industries.json', verbosity=0)
        call_command('loaddata', 'peeldb/fixtures/qualification.json', verbosity=0)
        call_command('loaddata', 'peeldb/fixtures/functionalarea.json', verbosity=0)

        result = {'message': "Successfully Loading initial data"}

        return json.dumps(result)
