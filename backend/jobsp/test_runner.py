"""
Test runner that keeps the suite off Elasticsearch.

`HAYSTACK_SIGNAL_PROCESSOR` is `RealtimeSignalProcessor`, so saving a `Skill`,
`City`, `User` or `JobPost` tries to index it in real time. Elasticsearch is not
part of this stack any more — nothing surviving reads from it — so every one of
those saves died with `ConnectionError: Connection refused`. That was 22 of the
suite's 23 long-standing errors, across `candidate/`, `pjob/`, `dashboard/` and
`api/v1/auth/`.

Doing this in the runner rather than per test class matters for two reasons:
it is one place instead of twelve, and 20 of the 23 erroring tests live in
`candidate/` and `pjob/`, which are slated for deletion — editing them would be
throwaway work, whereas this keeps working for whatever replaces them.

`override_settings` and patching `RealtimeSignalProcessor` on the class both
fail here: the processor is instantiated once in `HaystackConfig.ready()` and
connects its *bound* methods as signal receivers, so the receivers already hold
references to the original functions. Only `teardown()` on that live instance
disconnects them — the same handle the repo's own management commands use
(see `peeldb/management/commands/load_initial_data.py`).
"""

from django.apps import apps
from django.test.runner import DiscoverRunner
from haystack import connections

SIMPLE_ENGINE = "haystack.backends.simple_backend.SimpleEngine"


class NoSearchIndexingTestRunner(DiscoverRunner):
    """`DiscoverRunner` with haystack pointed away from Elasticsearch."""

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)

        self._original_engines = {}
        for alias, conn in connections.connections_info.items():
            self._original_engines[alias] = conn.get("ENGINE")
            conn["ENGINE"] = SIMPLE_ENGINE
            connections.reload(alias)

        try:
            processor = apps.get_app_config("haystack").signal_processor
        except LookupError:
            # haystack is not installed — nothing to disconnect.
            return

        if processor is not None:
            processor.teardown()
            self._haystack_processor = processor

    def teardown_test_environment(self, **kwargs):
        processor = getattr(self, "_haystack_processor", None)
        if processor is not None:
            # Restore, so anything running in the same process afterwards
            # behaves as configured.
            processor.setup()

        for alias, engine in getattr(self, "_original_engines", {}).items():
            connections.connections_info[alias]["ENGINE"] = engine
            connections.reload(alias)

        super().teardown_test_environment(**kwargs)
