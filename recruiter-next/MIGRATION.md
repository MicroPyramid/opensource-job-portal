# Recruiter UI Migration — SvelteKit → Next.js

Migrating `recruiter/` (SvelteKit 2 + Svelte 5) to `recruiter-next/` (Next.js 16 + React 19).
Both apps run side by side against the same Django backend until cutover.

| Service                    | Port   | Command                     |
| -------------------------- | ------ | --------------------------- |
| Django backend             | `8000` | `cd backend && uv run manage.py runserver` |
| `recruiter/` (SvelteKit)   | `5174` | `cd recruiter && pnpm dev`  |
| `recruiter-next/` (Next.js)| `3003` | `cd recruiter-next && pnpm dev -p 3003` |

Keeping both up is the whole verification strategy: every route gets diffed against the
running original before it's marked done.

---

## Status legend

| Mark | Meaning                                                      |
| ---- | ------------------------------------------------------------ |
| ⬜   | Not started                                                   |
| 🟡   | In progress                                                   |
| 🔍   | Built, awaiting parity check against `:5174`                  |
| ✅   | Done — parity verified, `pnpm build` + `tsc` clean            |
| ⏸️   | Blocked (reason in Notes)                                     |
| ⏭️   | Intentionally dropped (reason in Notes)                       |

## Progress dashboard

| Area                  | Done  | Total | Status |
| --------------------- | ----- | ----- | ------ |
| Phase 0 — Foundation  | 7     | 7     | ✅     |
| Styling & tokens      | 3     | 3     | ✅     |
| UI primitives         | 0     | 8     | ⬜     |
| Shared lib            | 1     | 9     | 🟡     |
| Layouts               | 0     | 3     | ⬜     |
| Pages                 | 1     | 21    | 🟡     |
| Route handlers        | 0     | 3     | ⬜     |
| Server actions        | 0     | 32    | ⬜     |
| **Overall**           | **12**| **86**| 🟡     |

Source scope: 55 files, ~14.3k LOC (9.5k Svelte, 4.8k TS).

---

## Stack decisions

Scaffolded already: **Next.js 16.3.0, React 19.2.8, Tailwind CSS 4, TypeScript 5, pnpm 11.19.0**.

> ⚠️ **Next.js 16 differs from older App Router material.** `recruiter-next/AGENTS.md` (written by
> `next dev`) says to read `node_modules/next/dist/docs/` before writing code. The v16 changes that
> actually bite this migration:
>
> | Change                     | Impact here                                                             |
> | -------------------------- | ----------------------------------------------------------------------- |
> | `middleware.ts` → `proxy.ts` | The auth guard from `hooks.server.ts` goes in **`proxy.ts`** at root     |
> | Async Request APIs         | `cookies()`, `headers()`, `params`, `searchParams` must all be `await`ed |
> | Turbopack by default       | No Vite config to port; dev/build already Turbopack                      |
> | `next lint` removed        | ESLint flat config only — `package.json` already has `"lint": "eslint"`  |
> | Caching APIs               | `revalidateTag` / `updateTag` / `refresh` replace ad-hoc invalidation    |

| Concern       | `recruiter/` (today)                     | `recruiter-next/` (target)                            |
| ------------- | ---------------------------------------- | ----------------------------------------------------- |
| Routing       | `+page.svelte` / route groups            | App Router, same `(auth)` / `(dashboard)` groups       |
| Data loading  | `+page.server.ts` `load()`                | `async` Server Components                              |
| Mutations     | Form actions + `use:enhance`              | Server Actions + `useActionState`                      |
| Auth guard    | `hooks.server.ts` `authGuard`             | `proxy.ts` (optimistic) + `requireAuth()` DAL (real)   |
| Auth fetch    | `hooks.server.ts` `apiHandler` wraps fetch| `serverFetch()` helper in `lib/api/client.ts`          |
| Styling       | Tailwind 4 `@theme` in `app.css`          | **Identical `@theme` block** in `app/globals.css`      |
| Icons         | `@lucide/svelte`                          | `lucide-react` (same icon names)                       |
| Deploy        | `adapter-node` → `node build`             | `output: 'standalone'` → `node server.js`              |
| Trailing slash| Always on                                 | `trailingSlash: true` in `next.config.ts` — **required** |

**Deliberately deferred:** no component library (shadcn/ui, Radix) in the first pass. The six
primitives get ported 1:1 so parity is reviewable against a running original. Swapping in a library
while also changing framework makes every visual diff ambiguous. Revisit once ✅ across the board.

**To add when the phase needs it:** `zod` (action input validation — currently hand-rolled),
`clsx` + `tailwind-merge` (the primitives concatenate class strings by hand today).

---

## Phase 0 — Foundation

| Status | Task                                                                                  |
| ------ | ------------------------------------------------------------------------------------- |
| ✅     | Scaffold `recruiter-next/` with create-next-app (Next 16.3.0, TS, Tailwind 4, pnpm)    |
| ✅     | Strip CNA boilerplate: `app/page.tsx`, `public/*.svg`, Geist fonts in `app/layout.tsx` |
| ✅     | `next.config.ts`: `trailingSlash: true`, `output: 'standalone'`, `images.remotePatterns` for Django media |
| ✅     | `.env.example` + `.env` — see [Environment](#environment) (rename `PUBLIC_*` → `NEXT_PUBLIC_*`) |
| ✅     | `pnpm add lucide-react zod clsx tailwind-merge` (+ `server-only`, Tailwind plugins)     |
| ✅     | `lib/config/env.ts` — port with the `getApiBasePath()` dead path dropped               |
| ✅     | Add `"dev": "next dev -p 3003"` to `package.json` so the port isn't a flag every time  |

**Also done in this phase, beyond the original list:**

- `.gitignore`: added `!.env.example` — CNA's blanket `.env*` would have kept the example file
  out of version control.
- `package.json`: `"typecheck": "tsc --noEmit"` (the parity gate needs it), `"start"` pinned to 3003.
- `lib/config/env.ts`: added `apiUrl(endpoint)` — the single chokepoint every Django call goes
  through, so debt #1 can't reappear. Missing env vars throw at import with a message pointing at
  `.env.example`, rather than silently producing `undefined/api/v1` URLs.
- `MEDIA_HOSTNAME` env var: `next/image` needs the S3 host allow-listed in production, and it's
  bucket-name-dependent (`AWS_S3_CUSTOM_DOMAIN` in `settings_server.py`). Dev pattern is derived
  from `API_BASE_URL`, so nothing is hardcoded.

### Phase 0 verification

| Check                                | Result                                                       |
| ------------------------------------ | ------------------------------------------------------------ |
| `pnpm typecheck`                     | ✅ clean                                                      |
| `pnpm build`                         | ✅ compiled in 1.8s; `/` correctly marked `ƒ` (dynamic)       |
| `GET /`                              | ✅ `307 → /login/` (entry redirect + cookie read working)      |
| `GET /login` (no slash)              | ✅ `308 → /login/` (`trailingSlash` active)                    |
| Design tokens in CSS bundle          | ✅ all 11 `--color-*` + `--font-sans` emitted                  |
| `@tailwindcss/forms` base reset      | ✅ 20 `[type=…]` selectors present                             |
| CNA leftovers (Geist, dark mode)     | ✅ 0 occurrences of `geist`, `prefers-color-scheme`, `--foreground` |

### Environment

`$env/static/public` → `process.env`. SvelteKit's `PUBLIC_` prefix becomes `NEXT_PUBLIC_`, but most
of these should stop being public at all — only the server talks to Django.

| `recruiter/`               | `recruiter-next/`      | Notes                                        |
| -------------------------- | ---------------------- | -------------------------------------------- |
| `PUBLIC_API_BASE_URL`      | `API_BASE_URL`         | Server-only now — no browser fetches Django   |
| `PUBLIC_SITE_URL`          | `NEXT_PUBLIC_SITE_URL` | Needed client-side for OAuth callback URLs    |
| —                          | `NODE_ENV`             | Drives the `secure` cookie flag (see debt #2) |

---

## Styling

The design system is defined in `/DESIGN_SYSTEM.md` (repo root) and implemented as a Tailwind 4
`@theme` block. **Both apps run Tailwind 4, so the token block copies across verbatim** — no
rewriting to `tailwind.config.js`, no renamed utilities. This is the cheapest part of the migration.

| Status | Task                                                                                          |
| ------ | --------------------------------------------------------------------------------------------- |
| ✅     | Copy the `@theme` block from `recruiter/src/app.css` into `app/globals.css` unchanged          |
| ✅     | **Delete CNA's `@theme inline`** — the `--background`/`--foreground` + `prefers-color-scheme` dark block. The recruiter UI has no dark mode; leaving it in silently inverts surfaces on dark-mode machines |
| ✅     | Port base styles: `scroll-behavior`, font smoothing, `*:focus-visible` outline                 |

### Tokens (carried over as-is)

| Token                    | Value     | Utility              |
| ------------------------ | --------- | -------------------- |
| `--color-primary`        | `#0A66C2` | `bg-primary`         |
| `--color-primary-hover`  | `#004182` | `hover:bg-primary-hover` |
| `--color-muted`          | `#666666` | `text-muted`         |
| `--color-border`         | `#E5E5E5` | `border-border`      |
| `--color-surface`        | `#F5F5F5` | `bg-surface`         |
| `--color-success`        | `#057642` | `text-success`       |
| `--color-success-light`  | `#DFF2E7` | `bg-success-light`   |
| `--color-warning`        | `#915907` | `text-warning`       |
| `--color-warning-light`  | `#FCF0DC` | `bg-warning-light`   |
| `--color-error`          | `#CC1016` | `text-error`         |
| `--color-error-light`    | `#FBEAEB` | `bg-error-light`     |
| `--font-sans`            | system stack | `font-sans`       |

> Font note: CNA wired up Geist via `next/font/google`. The design system specifies a **system font
> stack** (`-apple-system, BlinkMacSystemFont, 'Segoe UI', …`). Drop Geist — it changes the look and
> adds a network font the original never loaded.

### Plugins

`@plugin '@tailwindcss/forms'` and `@plugin '@tailwindcss/typography'` are used by `app.css`.
Install both and re-declare in `globals.css`, or form controls lose their reset.

### UI primitives — `recruiter/src/lib/components/ui/` → `components/ui/`

| Status | Component   | LOC | Porting notes                                                                             |
| ------ | ----------- | --- | ----------------------------------------------------------------------------------------- |
| ⬜     | `Button`    | 91  | Renders `<a>` when `href` set → use `next/link`. `Snippet` children → `React.ReactNode`. Spinner SVG copies over |
| ⬜     | `Input`     | 60  | `bind:value` → controlled `value`/`onChange`. Keep `Omit<…,'size'>` — `size` is the visual scale, not the native attr |
| ⬜     | `Card`      | 38  | Straight port                                                                              |
| ⬜     | `Badge`     | 38  | Straight port                                                                              |
| ⬜     | `Avatar`    | 64  | Initials fallback logic copies over. Evaluate `next/image` for the `src` branch            |
| ⬜     | `FormField` | 41  | Fix the a11y suppression: `useId()` to bind `<label htmlFor>` to the control (today it's `svelte-ignore a11y_label_has_associated_control`) |
| ⬜     | `index.ts`  | 6   | Barrel export                                                                              |
| ⬜     | `ApplicantDetailModal` | 409 | No focus trap / no Esc handling today. Real candidate for Radix Dialog — flag before hand-rolling |

### Svelte 5 → React 19 idiom map

| Svelte 5                       | React 19                                  |
| ------------------------------ | ----------------------------------------- |
| `$props()`                     | function params                            |
| `$state(x)`                    | `useState(x)`                              |
| `$derived(expr)`               | plain `const` (or `useMemo` if expensive)  |
| `$bindable()`                  | `value` + `onChange` pair                  |
| `{#snippet}` / `{@render}`     | `children` / render props                  |
| `{#each xs as x (x.id)}`       | `xs.map(x => <… key={x.id}>)`              |
| `onclick={fn}`                 | `onClick={fn}`                             |
| `class:active={cond}`          | `clsx('base', cond && 'active')`           |
| `<svelte:head>`                | `export const metadata` / `generateMetadata` |
| `$app/stores` `page`           | `usePathname()` / `useSearchParams()`      |
| `goto()`                       | `redirect()` (server) / `useRouter()` (client) |
| `use:enhance` + `form` prop    | `useActionState(action, initialState)`     |
| `fail(400, {...})`             | return `{ error }` from the action         |
| `invalidateAll()`              | `revalidatePath()` / `router.refresh()`    |

---

## Routes

`(auth)` and `(dashboard)` route groups map to App Router groups with the same names and semantics.
**`trailingSlash: true` is mandatory** — every internal link in the app is written `/dashboard/jobs/`.

### Root

| Status | SvelteKit                                    | LOC   | Next.js target        | Actions | Notes                    |
| ------ | -------------------------------------------- | ----- | --------------------- | ------- | ------------------------ |
| 🔍     | `routes/+layout.svelte`                      | 12    | `app/layout.tsx`      | –       | CNA boilerplate replaced. Favicon still CNA's `app/favicon.ico` — the original `lib/assets/favicon.svg` is a 0-byte file, so there's nothing to port |
| ✅     | `routes/+page.{server.ts,svelte}`            | 15+8  | `app/page.tsx`        | –       | Entry redirect. Verified `307 → /login/`. The original's "Redirecting…" spinner isn't needed — the redirect is issued before any HTML is sent |

### `(auth)` — 6 pages, 1 layout

| Status | SvelteKit                              | LOC     | Next.js target                    | Server actions               |
| ------ | -------------------------------------- | ------- | --------------------------------- | ---------------------------- |
| ⬜     | `(auth)/+layout.svelte`                | 48      | `app/(auth)/layout.tsx`           | –                            |
| ⬜     | `(auth)/login/`                        | 102+248 | `app/(auth)/login/`               | `login`                      |
| ⬜     | `(auth)/signup/`                       | 216+628 | `app/(auth)/signup/`              | `register`, `acceptInvitation` |
| ⬜     | `(auth)/forgot-password/`              | 47+120  | `app/(auth)/forgot-password/`     | `requestReset`               |
| ⬜     | `(auth)/reset-password/`               | 87+202  | `app/(auth)/reset-password/`      | `resetPassword`              |
| ⬜     | `(auth)/verify-email/`                 | 120+172 | `app/(auth)/verify-email/`        | `resend`                     |
| ⬜     | `(auth)/onboarding/`                   | 108+372 | `app/(auth)/onboarding/`          | `complete`, `skip`           |

### `(dashboard)` — 15 pages, 1 layout

| Status | SvelteKit                                     | LOC       | Next.js target                                  | Server actions                          |
| ------ | --------------------------------------------- | --------- | ----------------------------------------------- | --------------------------------------- |
| ⬜     | `(dashboard)/+layout.{server.ts,svelte}`      | 45+184    | `app/(dashboard)/layout.tsx` + `components/dashboard/Sidebar.tsx` | – |
| ⬜     | `dashboard/`                                  | 40+237    | `app/(dashboard)/dashboard/`                    | –                                       |
| ⬜     | `dashboard/jobs/`                             | 175+516   | `app/(dashboard)/dashboard/jobs/`               | `publish`, `close`, `delete`            |
| ⬜     | `dashboard/jobs/new/`                         | 352+1341  | `app/(dashboard)/dashboard/jobs/new/`           | `saveDraft`, `publish`                  |
| ⬜     | `dashboard/jobs/inactive/`                    | 169+311   | `app/(dashboard)/dashboard/jobs/inactive/`      | `reactivate`, `delete`                  |
| ⬜     | `dashboard/jobs/[id]/`                        | 136+432   | `app/(dashboard)/dashboard/jobs/[id]/`          | `toggleNotifications`                   |
| ⬜     | `dashboard/jobs/[id]/edit/`                   | 343+830   | `…/jobs/[id]/edit/`                             | `saveDraft`, `publish`                  |
| ⬜     | `dashboard/jobs/[id]/preview/`                | 44+308    | `…/jobs/[id]/preview/`                          | –                                       |
| ⬜     | `dashboard/jobs/[id]/applicants/`             | 126+405   | `…/jobs/[id]/applicants/`                       | `updateStatus`                          |
| ⬜     | `dashboard/company/`                          | 96+337    | `app/(dashboard)/dashboard/company/`            | `updateCompany`                         |
| ⬜     | `dashboard/company/microsite/`                | 256+459   | `…/company/microsite/`                          | `createMenu`, `updateMenu`, `deleteMenu`, `toggleMenuStatus` |
| ⬜     | `dashboard/team/`                             | 334+697   | `app/(dashboard)/dashboard/team/`               | `inviteMember`, `updateMember`, `removeMember`, `resendInvitation`, `cancelInvitation`, `toggleStatus` |
| ⬜     | `dashboard/team/[id]/`                        | 55+259    | `…/team/[id]/`                                  | –                                       |
| ⬜     | `dashboard/analytics/`                        | 34+349    | `app/(dashboard)/dashboard/analytics/`          | –                                       |
| ⬜     | `dashboard/account/`                          | 125+330   | `app/(dashboard)/dashboard/account/`            | `updateProfile`, `uploadPicture`        |

> `dashboard/jobs/new/+page.svelte` is **1341 lines** — the single largest file in the app, and
> `jobs/[id]/edit` (830) is largely the same form. Port `new/` first, extract the shared form into
> `components/jobs/JobForm.tsx`, then `edit/` should be thin. Do not port them independently.

> `(dashboard)/dashboard/team/+page.ts` (57 lines) is **type definitions, not a load function** —
> a misuse of the `+page.ts` convention. Move to `lib/types/team.ts`.

### Route handlers

| Status | SvelteKit                                      | LOC | Next.js target                            | Notes                                              |
| ------ | ---------------------------------------------- | --- | ----------------------------------------- | -------------------------------------------------- |
| ⬜     | `api/auth/set-cookies/+server.ts`              | 35  | `app/api/auth/set-cookies/route.ts`       | Likely ⏭️ — Server Actions can set cookies directly |
| ⬜     | `api/auth/clear-cookies/+server.ts`            | 16  | `app/api/auth/clear-cookies/route.ts`     | Likely ⏭️ — same                                    |
| ⬜     | `dashboard/jobs/[id]/applicants/download/+server.ts` | 134 | `…/applicants/download/route.ts`     | CSV export — must stay a route handler              |

---

## Auth architecture

The JWT model is unchanged: **Django issues JWTs → Next stores them in HttpOnly cookies → server
adds `Authorization: Bearer` when calling `/api/v1/`.** The browser never holds a token and never
calls Django directly. What changes is where each piece lives.

| Status | Concern            | `recruiter/`                                         | `recruiter-next/`                                          |
| ------ | ------------------ | ---------------------------------------------------- | ---------------------------------------------------------- |
| ⬜     | Route guard        | `hooks.server.ts` → `authGuard`                      | `proxy.ts` — optimistic cookie-presence check only          |
| ⬜     | Real authorization | Re-checked in each `+page.server.ts`                 | `requireAuth()` DAL, called in layout + **every action**     |
| ⬜     | Bearer injection   | `hooks.server.ts` → `apiHandler` monkey-patches `event.fetch` | `serverFetch()` in `lib/api/client.ts`             |
| ⬜     | Cookie set/clear   | Login action + `/api/auth/{set,clear}-cookies`       | `await cookies()` inside the Server Action                   |
| ⬜     | User for UI        | `+layout.server.ts` load → `authStore` localStorage mirror | Fetched in `app/(dashboard)/layout.tsx`, passed as props |
| ⬜     | Logout             | `authStore.logout()` → 2 endpoints + Django call     | `logout` Server Action                                       |

Three things to get right:

1. **`proxy.ts` is not authorization.** The v16 docs are explicit that proxy is for optimistic
   checks, not session management. It redirects `/dashboard/*` without cookies to `/login/`; the
   authoritative check lives in the DAL.
2. **Every Server Action re-authenticates.** Actions are reachable by direct POST, not just through
   your UI. `requireAuth()` goes at the top of all 32 — this is stricter than the current app, where
   several actions rely on the guard having already run.
3. **`authStore` (166 LOC) goes away.** It mirrors the user into `localStorage` and re-syncs on
   mount to work around not having server-rendered user state. The `(dashboard)` layout is a Server
   Component that fetches the user per request — the mirror has no job. Sidebar gets `user` as a prop.

---

## Shared lib

| Status | `recruiter/src/lib/`          | LOC | Target                           | Notes                                                    |
| ------ | ----------------------------- | --- | -------------------------------- | -------------------------------------------------------- |
| ⬜     | `types/index.ts`              | 458 | `lib/types/index.ts`             | Framework-free — copies verbatim                          |
| ⬜     | `api/client.ts`               | 215 | `lib/api/client.ts`              | Rewrite as server-only `serverFetch`; see debt #4         |
| ⬜     | `api/jobs.ts`                 | 128 | `lib/api/jobs.ts`                |                                                           |
| ⬜     | `api/auth.ts`                 | 104 | `lib/api/auth.ts`                |                                                           |
| ⬜     | `api/team.ts`                 | 88  | `lib/api/team.ts`                |                                                           |
| ⬜     | `api/profile.ts`              | 45  | `lib/api/profile.ts`             |                                                           |
| ⬜     | `utils/error-formatter.ts`    | 92  | `lib/utils/error-formatter.ts`   | Framework-free — copies verbatim                          |
| ✅     | `config/env.ts`               | 47  | `lib/config/env.ts`              | Ported. `getApiBasePath()` dropped; added `apiUrl()` + fail-fast on missing vars |
| ⬜     | `stores/auth.ts`              | 166 | ⏭️ **deleted**                    | Replaced by server-fetched user (see Auth #3)             |

---

## Debt to fix during migration

Found while auditing `recruiter/`. These are bugs in the current app — porting them 1:1 carries them
forward, so each is fixed as its route is migrated.

| # | Severity | Issue                                                                                                          | Fix                                                    |
| - | -------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 1 | **High** | **`http://localhost:8000` hardcoded** at 17 call sites across 6 server files (`jobs/`, `jobs/new/`, `jobs/[id]/edit/`, `jobs/inactive/`, `analytics/`, `dashboard/`). Breaks any non-local deploy | All API access goes through `serverFetch()` + `API_BASE_URL` |
| 2 | **High** | `secure: false` hardcoded on both auth cookies (`login/+page.server.ts`, `set-cookies/+server.ts`) with a "set to true in production" comment that was never actioned — JWTs sent over plain HTTP | `secure: process.env.NODE_ENV === 'production'`         |
| 3 | Medium   | Auth checked in three places: `hooks.server.ts` guard, `+layout.server.ts`, and again per-route in `+page.server.ts` — with slightly different redirect targets (`/login/` vs `/login?redirect=…`) | One `proxy.ts` + one `requireAuth()`             |
| 4 | Medium   | `api/client.ts` carries a client-side token-refresh queue (`isRefreshing`, `refreshSubscribers`) that can't work — the tokens are HttpOnly, so the browser can't read them to refresh | Refresh moves server-side; delete the queue      |
| 5 | Medium   | `corsHandler` in `hooks.server.ts` answers every `OPTIONS` with `Access-Control-Allow-Origin: *`. Nothing cross-origin should be hitting this app | ⏭️ Don't port                                     |
| 6 | Low      | `login/+page.server.ts` detects redirects via `(error as any)?.status === 302` inside a `catch` | Server Action `redirect()` throws a typed signal — just don't catch it |
| 7 | Low      | `getApiBasePath()` is `@deprecated` but still exported and used by `api/client.ts`                             | Drop it                                                 |
| 8 | Low      | `FormField` label isn't bound to its control (`svelte-ignore a11y_label_has_associated_control`)                | `useId()`                                               |
| 9 | Low      | **Zero tests** in the app — no safety net for this migration                                                    | See below                                               |

> On #9: the parity protocol below is the substitute for a test suite. It's manual. If a route's
> behaviour is subtle (the job form, team invitations), write a Playwright spec for it *before*
> porting rather than after — that's the only way that route gets checked twice.

---

## Parity verification

No route is ✅ until all four pass:

1. **Side-by-side** — same path on `:5174` and `:3003`, same backend, same logged-in recruiter.
   Compare rendered output, not just "it loads."
2. **View source** — content is present in the initial HTML. A route that renders only after
   hydration has lost the SSR the original had.
3. **Every action exercised** — success path *and* the validation-failure path. The error shape
   returned by `useActionState` must match what the original showed via `fail()`.
4. **Clean** — `pnpm build` and `pnpm exec tsc --noEmit` with no new errors.

Per-phase gate: `pnpm build` must pass before moving to the next phase. Don't accumulate broken
routes behind a green dev server — Turbopack dev is more forgiving than the production build.

---

## Cutover

Not scheduled yet. Preconditions:

- [ ] All 21 pages, 3 layouts, 3 route handlers ✅
- [ ] All 32 server actions exercised both paths
- [ ] Debt items #1–#5 fixed
- [ ] `output: 'standalone'` build runs behind the existing nginx config (see `/SETUP.md`)
- [ ] Deploy runbook updated: `node build` → `node server.js`, port `5174` → `3003`
- [ ] `recruiter/` kept in the tree for one release as rollback, then removed in a separate commit

`site/` stays on SvelteKit. It's the SEO surface and its payload budget matters more; nothing here
applies to it.

---

## Progress log

Newest first. One line per session — what moved, what broke, what's next.

| Date       | Change                                                                 |
| ---------- | ---------------------------------------------------------------------- |
| 2026-08-11 | **Phase 0 + styling complete (12/86).** Config, env, tokens, entry redirect all verified against the running dev server. Deps added: `lucide-react`, `zod`, `clsx`, `tailwind-merge`, `server-only`, Tailwind forms/typography. Next: `lib/api/client.ts` (`serverFetch`) + `proxy.ts` — everything downstream depends on those two. |
| 2026-08-11 | `recruiter-next/` scaffolded (Next 16.3.0). Audited `recruiter/`, wrote this plan. |
