# Search

PeelJobs searches jobs with PostgreSQL full-text search. There is no
Elasticsearch, no Solr, and no indexing service to run or keep alive.

!!! info "This replaced Elasticsearch"

    Earlier versions used Haystack with Elasticsearch. It was removed: at this
    corpus size — roughly 13,000 live jobs in a 33 MB table — Elasticsearch was
    three orders of magnitude oversized for the job, and Haystack was blocking
    the Django upgrade path by capping the Elasticsearch client below 8.x.

    If you find `HAYSTACKURL` in `.env.example` or an `update_index` command in
    an old guide, both are dead.

## How it works

`JobPost.search_vector` is a **generated column**: PostgreSQL computes and
stores it as part of the same transaction that writes the row.

```python
search_vector = models.GeneratedField(
    expression=(
        SearchVector("title",        weight="A", config="english")
        + SearchVector("job_role",     weight="B", config="english")
        + SearchVector("company_name", weight="C", config="english")
        + SearchVector("description",  weight="D", config="english")
    ),
    output_field=SearchVectorField(),
    db_persist=True,
)
```

Weights rank a title match above a description match:

| Weight | Field |
| --- | --- |
| A | `title` |
| B | `job_role` |
| C | `company_name` |
| D | `description` |

**There is no reindex step.** Edit a job and it is immediately searchable,
because the database maintains the column itself. That is the whole reason for
choosing a generated column over a trigger or a Django signal: the index cannot
drift from the data, which is exactly the failure mode the old Haystack signal
processor existed to paper over.

## Indexes

| Index | Backs |
| --- | --- |
| `jobpost_search_vector_gin` | Full-text matching on `search_vector` |
| `jobpost_title_trgm_gin` | Trigram fallback on `title` |

Both are created by migration `0080_jobpost_search_vector`;
`0079_pg_trgm_extension` enables `pg_trgm`. They are split so that a
`CREATE EXTENSION` permissions failure is unambiguous — see
[Installation](../getting-started/installation.md).

## Query behaviour

`api/v1/jobs/filters.py` handles `?search=`:

1. Parse the term with `websearch_to_tsquery`, so quoting and `or`/`-` work the
   way users expect from a search box.
2. Match against `search_vector`, annotate with `SearchRank`.
3. **If — and only if — that returns nothing**, fall back to trigram word
   similarity on `title` above a threshold of `0.4`.

The fallback is deliberately last-resort. Running trigram similarity alongside
full-text results would drag in loose matches and dilute good ones; running it
only on zero results means `pyhton` still finds Python jobs while `java` keeps
returning clean Java results.

The `0.4` threshold is measured, not guessed. At `0.3`, `mangaer` matches 916
jobs and a city lookup for `manipur` starts surfacing unrelated names; at `0.4`
the same typo matches 12.

### Ordering

`RelevanceOrderingFilter` sorts by relevance when a search term is present and
by `-published_on` otherwise. An explicit `?ordering=` always wins.

### What full-text search changes

Two results surprise people:

- **Searching `java` returns fewer jobs than substring matching did.** That is
  correct. `icontains` matched the `java` inside "JavaScript", so a Java search
  returned front-end jobs. Full-text search tokenises and does not.
- **Searching `manager` returns more.** English stemming folds "managing",
  "managers" and "management" to the same root. Those were always relevant;
  substring matching could not see them.

## Autocomplete

Skill and location lookups use a shared helper,
`api/v1/common/search.py:fuzzy_name_filter`, with the same
substring-first-then-trigram shape:

1. `icontains` match — because an autocomplete sends fragments, and trigram
   similarity scores `pyt` against `Python` poorly.
2. Only if that is empty, trigram word similarity above `0.4`.

Substring hits sort alphabetically; fallback hits sort by closeness, so the
intended answer is not buried.

Neither table is indexed for this. At 866 skills and 113 cities a sequential
scan is microseconds, and an index would be dead weight.

## Performance

Measured on the development corpus, query time only:

| Query | Before (icontains) | After (FTS) |
| --- | --- | --- |
| `python developer` | 63 hits, 99.4 ms | 204 hits, 1.5 ms |
| `java` | 1913 hits, 77.3 ms | 1096 hits, 0.9 ms |
| `pyhton` | 0 hits, 85.7 ms | 1 hit, 0.3 ms |
| `manager` | 1493 hits, 78.1 ms | 3516 hits, 2.0 ms |

End to end an API search runs 43–86 ms, dominated by serialising results and
their prefetches. Search is no longer the expensive part of the request.

## Deliberately left alone

Company lookups (`api/v1/companies/views.py`) and the recruiter-side lookups
still use `icontains`. They are scoped to small, already-filtered result sets
where full-text search would add complexity without measurable benefit.

## Operations

Nothing to run. No indexing daemon, no cron job, no `update_index` command. The
only operational requirement is that `pg_trgm` is installed, which migration
`0079` handles.
