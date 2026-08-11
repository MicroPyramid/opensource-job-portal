# Recruiter Routes

| URL | Purpose | Design System |
|-----|---------|---------------|
| `/` | Root redirect to `/dashboard/` | N/A |
| `/login/` | Recruiter login page | Done |
| `/signup/` | Account registration | Done |
| `/onboarding/` | Post-signup company setup | Done |
| `/forgot-password/` | Password recovery | Done |
| `/reset-password/` | Password reset form | Done |
| `/verify-email/` | Email verification | Done |
| `/dashboard/` | Main dashboard with stats overview | Done |
| `/dashboard/jobs/` | Job listings with filters | Done |
| `/dashboard/jobs/new/` | Create new job posting | Done |
| `/dashboard/jobs/inactive/` | View inactive jobs | Done |
| `/dashboard/jobs/[id]/` | Job detail page | Done |
| `/dashboard/jobs/[id]/edit/` | Edit job posting | Done |
| `/dashboard/jobs/[id]/preview/` | Preview job listing | Done |
| `/dashboard/jobs/[id]/applicants/` | Manage job applicants | Done |
| `/dashboard/jobs/[id]/applicants/download/` | Download applicants list | N/A |
| `/dashboard/company/` | Company profile settings | Done |
| `/dashboard/company/microsite/` | Company microsite settings | Done |
| `/dashboard/team/` | Team members management | Done |
| `/dashboard/team/[id]/` | Team member details | Done |
| `/dashboard/analytics/` | Hiring analytics dashboard | Done |
| `/dashboard/account/` | User account settings | Done |
| `/api/auth/set-cookies/` | Set JWT auth cookies | N/A |
| `/api/auth/clear-cookies/` | Clear auth cookies on logout | N/A |

## Components Updated

| Component | Path | Status |
|-----------|------|--------|
| ApplicantDetailModal | `$lib/components/recruiter/ApplicantDetailModal.svelte` | Done |
| Button | `$lib/components/ui/Button.svelte` | Done |
| Card | `$lib/components/ui/Card.svelte` | Done |
| Badge | `$lib/components/ui/Badge.svelte` | Done |
| Input | `$lib/components/ui/Input.svelte` | Done |
| FormField | `$lib/components/ui/FormField.svelte` | Done |
| Avatar | `$lib/components/ui/Avatar.svelte` | Done |
