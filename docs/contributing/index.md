# Contributing

PeelJobs is MIT-licensed and open to contributions.

Start with [Installation](../getting-started/installation.md), then
[Architecture](../architecture/index.md) — particularly
[Authentication](../architecture/authentication.md), which is where most
misunderstandings begin.

## Workflow

1. **Open an issue** first, unless one exists. For bugs, include reproduction
   steps and the version you saw it on.
2. **Branch from `master`.** Do not work directly on it.

    ```bash
    git checkout -b fix/master/my-contribution master
    ```

3. **Make focused commits.** One logical change each.
4. **Add tests.** See [Testing](testing.md).
5. **Run the suite** before pushing — not just your own tests.
6. **Format and lint:**

    ```bash
    cd backend
    uv run ruff format .
    uv run ruff check .
    ```

7. **Check for stray whitespace:**

    ```bash
    git diff --check
    ```

8. **Open a pull request** describing what changed and why.

## Commit messages

A subject line in the imperative, then a body explaining the behaviour without
the patch, why that is a problem, and how the patch fixes it.

```
Make the CONTRIBUTING example imperative and concrete

Without this patch the example commit message in the CONTRIBUTING document
is not a concrete example. This is a problem because the contributor is left
to imagine what the commit message should look like based on a description
rather than an example. This patch fixes the problem by making the example
concrete and imperative.
```

## Where changes belong

| Change | Goes in |
| --- | --- |
| API endpoint, model, task | `backend/` |
| Job seeker UI | `site/` |
| Recruiter UI | `recruiter/` |
| Docs | `docs/` |

!!! warning "Do not improve `backend/templates/`"

    The Django templates are being replaced by the SvelteKit apps. Styling
    fixes, Bootstrap→Tailwind conversion and markup cleanup there will be
    deleted along with the templates.

    The way to modernise one of those pages is to rewrite it in `site/` or
    `recruiter/`. The `/api/v1/` API is **not** legacy and is actively
    maintained.

## Good first areas

- Bug fixes
- Search quality
- Mobile experience
- Accessibility
- Migrating a remaining Django template page to SvelteKit
- Test coverage
- These docs

## Security

Do not open a public issue for a security vulnerability. See the repository's
`SECURITY.md` for how to report privately.

## Reference

- [Code Standards](code-standards.md)
- [Testing](testing.md)
- [Architecture](../architecture/index.md)
