"""Enable pg_trgm, which backs the typo-tolerant fallback in job search.

Split out from the schema change that uses it (0080) because `CREATE EXTENSION`
needs privileges the migrating role may not have in every environment. Keeping
it alone means a permissions failure here is obvious, rather than surfacing as a
confusing failure part-way through an index build.

Postgres 16.14 on this deployment has pg_trgm available but not installed;
`TrigramExtension` issues `CREATE EXTENSION IF NOT EXISTS`, so re-running is
safe. `unaccent` was considered and deliberately left out: nothing in the search
path folds diacritics, so installing it would be dead weight.
"""

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("peeldb", "0078_alter_user_registered_from"),
    ]

    operations = [
        TrigramExtension(),
    ]
