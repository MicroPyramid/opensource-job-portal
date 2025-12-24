from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
import json


class Command(BaseCommand):
    args = "<filename>"
    help = "Loads the initial data in to database"

    def handle(self, *args, **options):
        # Temporarily disconnect Haystack signals to avoid Elasticsearch dependency
        signal_processor = apps.get_app_config("haystack").signal_processor
        signal_processor.teardown()

        try:
            call_command("loaddata", "peeldb/fixtures/countries.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/states.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/cities.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/skills.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/industries.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/qualification.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/functionalarea.json", verbosity=0)
            call_command("loaddata", "peeldb/fixtures/languages.json", verbosity=0)
            self.stdout.write(self.style.SUCCESS("Successfully loaded initial data"))
        finally:
            signal_processor.setup()

        result = {"message": "Successfully loaded initial data"}
        return json.dumps(result)
