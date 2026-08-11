# Site Routes Documentation

All routes for the PeelJobs job seeker frontend (`/site/`).

## Redesign Status

Implementing design system from `DESIGN_SYSTEM.md`.

| Status | Description       |
| ------ | ----------------- |
| ✅     | Redesign complete |
| 🔄     | In progress       |
| ⏳     | Pending           |

## Authentication Routes

| URL                      | Purpose                                                | Redesign Status |
| ------------------------ | ------------------------------------------------------ | --------------- |
| `/login/`                | User login with email/password and Google OAuth        | ✅              |
| `/register/`             | Multi-step registration for Job Seekers and Recruiters | ✅              |
| `/forgot-password/`      | Request password reset via email                       | ✅              |
| `/reset-password/`       | Set new password with reset token                      | ✅              |
| `/verify-email/`         | Email verification confirmation page                   | ✅              |
| `/auth/google/callback/` | OAuth callback handler for Google authentication       | N/A             |

## Job Routes

| URL           | Purpose                                                                     | Redesign Status |
| ------------- | --------------------------------------------------------------------------- | --------------- |
| `/`           | Home page with hero, job search, featured jobs, browse by category/location | ✅              |
| `/jobs/`      | Jobs listing with filters (skills, location, job type, salary, experience)  | ✅              |
| `/jobs/[id]/` | Job detail page with full info, apply button, related jobs                  | ✅              |

## Company Routes

| URL                | Purpose                                               | Redesign Status |
| ------------------ | ----------------------------------------------------- | --------------- |
| `/companies/`      | Companies listing with industry/location/size filters | ✅              |
| `/companies/[id]/` | Company detail page with info and active job listings | ✅              |

## User Dashboard Routes

| URL               | Purpose                                                                | Redesign Status |
| ----------------- | ---------------------------------------------------------------------- | --------------- |
| `/applications/`  | View applied jobs with status tracking (Under Review, Interview, etc.) | ✅              |
| `/saved/`         | Saved/bookmarked jobs management                                       | ✅              |
| `/messages/`      | Messages inbox with recruiter conversations                            | ✅              |
| `/messages/[id]/` | Individual message conversation thread                                 | ✅              |

## Profile Routes

All profile routes share a layout with navigation tabs.

| URL                        | Purpose                                                    | Redesign Status |
| -------------------------- | ---------------------------------------------------------- | --------------- |
| `/profile/`                | Main profile - personal info (name, email, location, etc.) | ✅              |
| `/profile/education/`      | Manage educational qualifications                          | ✅              |
| `/profile/skills/`         | Manage professional skills with proficiency levels         | ✅              |
| `/profile/employment/`     | Manage work history and job experiences                    | ✅              |
| `/profile/projects/`       | Showcase portfolio projects                                | ✅              |
| `/profile/certifications/` | Manage professional certifications                         | ✅              |

## Public Profile Route

| URL    | Purpose                                              | Redesign Status |
| ------ | ---------------------------------------------------- | --------------- |
| `/@u/` | Public user profile/resume view with download option | ✅              |

## Platform Pages

| URL         | Purpose                                                    | Redesign Status |
| ----------- | ---------------------------------------------------------- | --------------- |
| `/about/`   | Company mission, values, and team information              | ✅              |
| `/contact/` | Contact form for user inquiries                            | ✅              |
| `/privacy/` | Privacy policy (cookies, data collection, security)        | ✅              |
| `/terms/`   | Terms of Service (eligibility, conduct rules, user rights) | ✅              |
| `/pricing/` | Subscription plans for employers                           | ✅              |
| `/help/`    | FAQ and help documentation                                 | ✅              |

## Core Components Updated

| Component   | Location                                 | Status |
| ----------- | ---------------------------------------- | ------ |
| `app.css`   | `/site/src/app.css`                      | ✅     |
| Site Layout | `/site/src/routes/(site)/+layout.svelte` | ✅     |

## Route Structure Notes

- **Route Group `(site)`**: Most routes use the shared site layout with header/footer
- **Dynamic Routes**: `[id]` segments capture URL parameters (e.g., `/jobs/123/`)
- **Trailing Slashes**: All URLs end with `/` (e.g., `/jobs/` not `/jobs`)
- **SSR**: All pages are server-side rendered via `+page.server.ts` files

## Design System Reference

See `/DESIGN_SYSTEM.md` for:

- Color palette (Blue #0A66C2)
- Typography scale
- Component specifications
- Spacing patterns
- Accessibility requirements
