# Recruiter Platform - Authentication Pages

This document describes all authentication-related pages created for the PeelJobs recruiter/employer platform.

## Overview

The authentication flow follows industry standards similar to Naukri.com, Indeed.com, and other job platforms. All pages are mobile-responsive and follow the project's design system.

---

## Pages Created

### 1. **Sign Up** (`/signup/`)
Multi-step registration for new employer accounts.

**Features:**
- 3-step registration process:
  - **Step 1:** Company Information (name, industry, size, website)
  - **Step 2:** Personal Information (name, email, phone, job title)
  - **Step 3:** Account Setup (password with validation)
- Google OAuth integration
- Password strength validation
- Terms of service acceptance
- Newsletter subscription option
- Progress indicator
- Link to login page

**Flow:**
```
/signup/ → Complete 3 steps → Email verification → /onboarding/ → /dashboard/
```

---

### 2. **Login** (`/login/`)
Standard login page for existing users.

**Features:**
- Email/password authentication
- "Remember me" checkbox
- Google OAuth integration
- Forgot password link
- Sign up link for new users
- Link to job seeker login (separate platform)
- Show/hide password toggle

**Flow:**
```
/login/ → Authenticate → /dashboard/
```

---

### 3. **Forgot Password** (`/forgot-password/`)
Password reset request page.

**Features:**
- Email input for password reset
- Success state with confirmation message
- Resend email option
- Back to login link
- Spam folder reminder

**Flow:**
```
/forgot-password/ → Enter email → Check email → Click reset link → /reset-password/
```

---

### 4. **Reset Password** (`/reset-password/`)
Create new password after clicking reset link.

**Features:**
- New password input with validation
- Confirm password matching
- Real-time password strength indicator:
  - Minimum 8 characters
  - Uppercase letter
  - Lowercase letter
  - Number
- Visual validation checkmarks
- Show/hide password toggles
- Success state after reset
- Redirect to login

**Flow:**
```
/reset-password/?token=xyz → Create new password → /login/
```

---

### 5. **Email Verification** (`/verify-email/`)
Email verification after signup.

**Features:**
- Auto-verification on page load using token from URL
- Four states:
  - **Verifying:** Loading spinner
  - **Success:** Redirect to onboarding
  - **Expired:** Resend verification option
  - **Error:** Invalid token handling
- Resend verification email
- Skip to dashboard option

**Flow:**
```
Email → Click verification link → /verify-email/?token=xyz → /onboarding/
```

---

### 6. **Onboarding** (`/onboarding/`)
First-time setup wizard for new accounts (after email verification).

**Features:**
- 3-step guided setup:
  - **Step 1:** Complete company profile (logo, about, headquarters)
  - **Step 2:** Invite team members (optional)
  - **Step 3:** Hiring preferences (job categories, goals, monthly hires)
- Progress bar
- Logo upload
- Team invitation system
- Skip option
- Job category selection

**Flow:**
```
/onboarding/ → Complete 3 steps → /dashboard/
```

---

## Authentication Layout

All auth pages share a common layout (`(auth)/+layout.svelte`):

**Features:**
- Clean header with logo
- Centered card design
- Footer with links (About, Privacy, Terms, Contact)
- Maximum width constraint for readability
- Consistent branding

---

## Route Structure

```
recruiter_ui/src/routes/
├── (auth)/
│   ├── +layout.svelte           # Auth layout wrapper
│   ├── signup/
│   │   └── +page.svelte         # Multi-step signup
│   ├── login/
│   │   └── +page.svelte         # Login page
│   ├── forgot-password/
│   │   └── +page.svelte         # Request password reset
│   ├── reset-password/
│   │   └── +page.svelte         # Reset password with token
│   ├── verify-email/
│   │   └── +page.svelte         # Email verification
│   └── onboarding/
│       └── +page.svelte         # First-time setup
└── (dashboard)/
    └── ...                       # Dashboard pages
```

---

## User Flows

### New User Registration
```
1. /signup/ → Fill 3-step form → Submit
2. Email sent → Check inbox
3. /verify-email/?token=xyz → Email verified
4. /onboarding/ → Complete profile (optional)
5. /dashboard/ → Start using platform
```

### Existing User Login
```
1. /login/ → Enter credentials → Submit
2. /dashboard/ → Access account
```

### Forgot Password
```
1. /login/ → Click "Forgot password?"
2. /forgot-password/ → Enter email → Submit
3. Email sent → Click reset link
4. /reset-password/?token=xyz → Create new password
5. /login/ → Sign in with new password
```

### OAuth (Google)
```
1. /signup/ or /login/ → Click "Continue with Google"
2. Google OAuth flow → Authorize
3. Account created/logged in
4. /onboarding/ (new users) or /dashboard/ (existing users)
```

---

## Features Summary

### ✅ Security
- Password strength validation
- Password confirmation
- Show/hide password toggles
- Token-based email verification
- Token-based password reset
- HTTPS required (production)

### ✅ User Experience
- Multi-step forms with progress indicators
- Clear error messages
- Success confirmations
- Loading states
- Skip options where appropriate
- Mobile-responsive design

### ✅ Social Auth
- Google OAuth integration
- Easy one-click signup/login

### ✅ Team Features
- Team member invitation during onboarding
- Role-based access (to be connected with backend)

---

## Backend Integration Required

These pages need to be connected to your Django REST API endpoints:

### Required API Endpoints

1. **POST /api/v1/auth/register/**
   - Create new employer account
   - Send verification email
   - Return JWT tokens

2. **POST /api/v1/auth/login/**
   - Authenticate user
   - Return JWT tokens
   - Set HttpOnly cookies

3. **POST /api/v1/auth/logout/**
   - Invalidate tokens
   - Clear cookies

4. **POST /api/v1/auth/forgot-password/**
   - Send password reset email with token

5. **POST /api/v1/auth/reset-password/**
   - Validate reset token
   - Update password

6. **POST /api/v1/auth/verify-email/**
   - Validate verification token
   - Mark email as verified

7. **GET /api/v1/auth/me/**
   - Get current user info
   - Check authentication status

8. **POST /api/v1/auth/google/**
   - Google OAuth callback
   - Create/login user
   - Return JWT tokens

9. **POST /api/v1/auth/resend-verification/**
   - Resend verification email

10. **POST /api/v1/onboarding/**
    - Save onboarding data
    - Update company profile

---

## Environment Variables

Add these to your `.env` file:

```env
# Google OAuth (for social login)
PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
PUBLIC_GOOGLE_REDIRECT_URI=http://localhost:5173/auth/google/callback
```

---

## Next Steps

1. **Create API client module** (`src/lib/api/auth.ts`)
   - Functions for each auth endpoint
   - Token management
   - Error handling

2. **Implement auth store** (`src/lib/stores/auth.ts`)
   - User state management
   - Authentication status
   - Token storage (cookies)

3. **Add route guards**
   - Protect dashboard routes (require auth)
   - Redirect to login if not authenticated
   - Redirect to dashboard if already authenticated

4. **Connect OAuth**
   - Setup Google OAuth credentials
   - Implement callback handler
   - Test OAuth flow

5. **Add form validation**
   - Client-side validation
   - Display API error messages
   - Handle network errors

6. **Testing**
   - Test all user flows
   - Test error states
   - Test mobile responsiveness

---

## Design References

Similar to:
- **Naukri Recruiter** (naukri.com/recruiter)
- **Indeed Employer** (employers.indeed.com)
- **LinkedIn Recruiter** (linkedin.com/talent)
- **Glassdoor Employer** (glassdoor.com/employers)

---

## Notes

- All passwords must be at least 8 characters with uppercase, lowercase, and numbers
- Email verification is required before full access
- Onboarding can be skipped but is recommended
- Google OAuth provides faster signup
- All pages are SSR-compatible (no client-only code in module scope)
- All forms use native HTML validation + custom validation
- All pages follow mobile-first responsive design

---

**Last Updated:** 2025-10-20
**Status:** Design Complete, Backend Integration Pending
