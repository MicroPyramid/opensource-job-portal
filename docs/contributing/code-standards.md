# Code Standards

## Python

Formatting and linting are both ruff. There is no separate black — `ruff format`
is Black-compatible, and ruff's defaults match Black's 88-column style, which is
why the project carries no `[tool.ruff]` style config.

```bash
cd backend
uv run ruff format .
uv run ruff check .
```

### Conventions

- Business logic in models and managers, not views.
- Use `select_related` and `prefetch_related` on anything that serialises
  relations. Job listing endpoints degrade badly without them.
- Configuration through environment variables and python-dotenv, never
  hardcoded.
- Never import `settings_local` from `settings.py`. See
  [Configuration](../getting-started/configuration.md) for what that broke.

### Suppressed lint rules

`backend/pyproject.toml` disables four rule groups. Each is a deliberate
decision, not unfinished work — read the comments there before re-enabling one.

| Rule | Why |
| --- | --- |
| `RUF012` | Fires ~284 times on Django/DRF idioms like `class Meta: fields = [...]`. Annotating them `ClassVar` is correct by the letter and pointless in practice. |
| `DTZ*` | The project runs `USE_TZ = False`, so Django itself returns naive datetimes. Making these calls aware would introduce real bugs. |
| `BLE001` | 68 sites where a bare `except:` was widened to `except Exception:`. Narrowing each needs knowing what it can actually raise — tracked as debt, not guessed at. |

## TypeScript and Svelte

```bash
cd site       # or recruiter
pnpm check
```

### Conventions

| Thing | Convention |
| --- | --- |
| Components | `PascalCase.svelte` |
| Files and folders | `kebab-case` |
| Functions | `camelCase` |
| Types | `PascalCase` |
| Events | `onclick={handler}` — Svelte 5, not `on:click` |
| Icons | `@lucide/svelte` |
| Styling | Tailwind, mobile-first: `text-sm md:text-base lg:text-lg` |

### Rules that are not negotiable

**SSR stays on.** Never `export const ssr = false`. Client-only code goes in
`onMount()`. The job seeker site exists to be indexed.

**Navigate with `<a href="/path/">`, not `goto()`.** An anchor is a crawlable
link; a `goto()` call is not.

**Trailing slashes always.** `/jobs/`, not `/jobs`. Standalone `+server.ts`
files do not inherit this and must set it themselves:

```ts
export const trailingSlash = 'always';
```

**Never call the Django API from the browser.** Reads go in `+page.server.ts`
`load()`, writes in `actions`. Use the `fetch` SvelteKit passes in — the global
one does not get the bearer header attached.

## Database

- Migrations are reviewed like code. Read the generated SQL with `sqlmigrate`
  before committing anything non-trivial.
- Split risky operations into their own migration. `pg_trgm` is enabled in
  `0079` separately from the column and indexes in `0080`, so a permissions
  failure points at one obvious cause.
- Prefer generated columns over triggers and signals where the database can
  maintain a value itself — see [Search](../architecture/search.md).

## Documentation

These docs are MkDocs Material in `docs/`.

```bash
pip install -r requirements-docs.txt
mkdocs serve          # live preview at http://127.0.0.1:8000
mkdocs build --strict # fail on broken links and warnings
```

Build with `--strict` before opening a PR; it turns broken internal links into
errors.

!!! danger "Never let `site_dir` fall back to its default"

    MkDocs defaults `site_dir` to `site/`, which in this repository is the
    SvelteKit job seeker application — and `mkdocs build` defaults to
    `--clean`, which empties `site_dir` first. `mkdocs.yml` sets `site_dir` to
    `_site` for exactly this reason. Do not remove it.
