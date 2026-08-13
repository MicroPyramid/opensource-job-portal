# Frontends

Two SvelteKit applications, both Svelte 5 + TypeScript + Tailwind CSS 4, both
built with `adapter-node`.

| App | Directory | Port | Audience |
| --- | --- | --- | --- |
| Job seeker site | `site/` | 5173 | Public. Job search, applications, alerts. |
| Recruiter dashboard | `recruiter/` | 5174 | Authenticated. Job posting, applicants. |

They are independent deployments that share only the API they call.

## Server-side rendering is mandatory

Neither app may disable SSR. `export const ssr = false` is not permitted
anywhere.

The job seeker site exists to be found in search results — a job listing that
renders only after a client-side fetch is a job listing search engines see as
an empty page. Client-only code belongs in `onMount()`.

## Calling the API

**Never call the Django API from component or browser code.** All API access
goes through the SvelteKit server:

- `+page.server.ts` `load()` for reads
- `+page.server.ts` `actions` for writes
- Client submits through `<form method="POST">` with `use:enhance`

```ts
// ❌ WRONG — from a component. Leaks the API surface to the browser and
//    has no access to the HttpOnly token.
const response = await fetch('/api/v1/profile', { method: 'PATCH' });
```

```ts
// ✅ CORRECT — +page.server.ts
export const actions = {
  updateProfile: async ({ request, fetch }) => {
    const data = await request.formData();
    return await fetch('/api/v1/recruiter/profile/update/', {
      method: 'PATCH',
      body: JSON.stringify(Object.fromEntries(data))
    }).then((r) => r.json());
  }
};
```

The `fetch` passed into `load` and `actions` is SvelteKit's instrumented
version. `hooks.server.ts` intercepts it and attaches
`Authorization: Bearer <token>` from the cookie — which is why using the global
`fetch` instead sends an unauthenticated request.

## Routing

File-based, under `src/routes/`.

### Job seeker site

Route groups separate concerns: `(site)` holds public pages, while `login`,
`register` and `logout` sit outside it.

SEO-shaped URLs are ordinary SvelteKit dynamic segments:

| Pattern | Example |
| --- | --- |
| `[skill]-jobs-in-[city]` | `/python-jobs-in-bangalore/` |
| `[industry]-industry-jobs` | `/finance-industry-jobs/` |
| `[company]-job-openings` | `/acme-job-openings/` |
| `fresher-jobs-in-[city]` | `/fresher-jobs-in-chennai/` |
| Job detail | `/{job-title-slug}-{id}/` |

There is also a `src/routes/api/` tree. These are *SvelteKit* endpoints, not
Django ones — thin server-side proxies for the few interactions that genuinely
need a client-side fetch, such as autocomplete.

### Recruiter dashboard

`(auth)` for login, signup, onboarding, email verification and password reset;
`(dashboard)` for the authenticated application.

### Trailing slashes

URLs always end in a slash: `/jobs/`, not `/jobs`.

!!! note "`+server.ts` files do not inherit `trailingSlash`"

    Standalone endpoint files do not pick up `trailingSlash` from
    `+layout.js`, so each one sets it explicitly:

    ```ts
    export const trailingSlash = 'always';
    ```

    Omitting it makes that endpoint redirect on every call.

## Conventions

| Thing | Convention |
| --- | --- |
| Components | `PascalCase.svelte` |
| Files and folders | `kebab-case` |
| Functions | `camelCase` |
| Types | `PascalCase` |
| Events | `onclick={handler}` — Svelte 5, not `on:click` |
| Icons | `@lucide/svelte` |
| Navigation | `<a href="/path/">`, not `goto()` |
| Styling | Mobile-first: `class="text-sm md:text-base lg:text-lg"` |

`<a href>` over `goto()` matters for the same reason SSR does: a real anchor is
a crawlable link, a `goto()` call is not.

## Shared code

```
src/lib/
├── api/          typed API clients
├── components/   shared Svelte components
├── server/       server-only code (auth.ts, api.ts, landing.ts)
└── stores/       Svelte stores
```

`src/lib/server/` is never bundled into the client. Anything touching tokens or
the API base URL belongs there.

## Commands

```bash
pnpm install
pnpm dev            # development server
pnpm check          # svelte-check type checking
pnpm build          # production build
pnpm start          # serve the build
```
