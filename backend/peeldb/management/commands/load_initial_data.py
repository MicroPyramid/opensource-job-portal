import json

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = "<filename>"
    help = "Loads the initial data in to database"

    def handle(self, *args, **options):
        call_command("loaddata", "peeldb/fixtures/countries.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/states.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/cities.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/skills.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/industries.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/qualification.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/functionalarea.json", verbosity=0)
        call_command("loaddata", "peeldb/fixtures/languages.json", verbosity=0)
        self.stdout.write(self.style.SUCCESS("Successfully loaded initial data"))

        result = {"message": "Successfully loaded initial data"}
        return json.dumps(result)
