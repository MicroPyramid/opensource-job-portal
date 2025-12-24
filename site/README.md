# PeelJobs Frontend - SvelteKit + TypeScript

Modern, fast, and type-safe frontend for PeelJobs Job Seeker platform.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm
- Django backend running on `localhost:8000`

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

Visit: **http://localhost:5173**

## 📁 Project Structure

```
ui/
├── src/
│   ├── routes/                    # SvelteKit pages (file-based routing)
│   │   ├── login/+page.svelte     # Login page
│   │   ├── auth/google/callback/  # Google OAuth callback
│   │   └── (site)/                # Protected routes group
│   │
│   ├── lib/                       # Shared code
│   │   ├── api/                   # API client modules
│   │   │   ├── client.ts          # Base HTTP client
│   │   │   └── auth.ts            # Authentication API
│   │   ├── stores/                # Svelte stores
│   │   │   └── auth.ts            # Auth state management
│   │   ├── types/                 # TypeScript types
│   │   ├── components/            # Shared components
│   │   └── utils/                 # Helper functions
│   │
│   ├── app.html                   # HTML template
│   └── app.css                    # Global styles
│
├── static/                        # Static assets
├── build/                         # Production build (generated)
└── README.md                      # This file
```

## 🔧 Configuration

### API Proxy (Development)

Vite proxies `/api/*` requests to Django:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

**Means:**
- Frontend request: `http://localhost:5173/api/v1/auth/me/`
- Proxies to: `http://localhost:8000/api/v1/auth/me/`

### Adapter

Using `adapter-node` for SSR:

```javascript
// svelte.config.js
adapter: adapter({
  out: 'build',
  precompress: false
})
```

## 🔐 Google OAuth Setup

### 1. Google Cloud Console

Add redirect URIs:
```
http://localhost:5173/auth/google/callback
https://yourdomain.com/auth/google/callback
```

See: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### 2. Django .env

Ensure these are set:
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_LOGIN_HOST=http://localhost:8000
```

### 3. Test Login Flow

**Terminal 1 - Django:**
```bash
cd /home/ashwin/git-prjs/peeljobs/peeljobs
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd /home/ashwin/git-prjs/peeljobs/peeljobs/ui
pnpm dev
```

**Test:**
1. Visit: http://localhost:5173/login
2. Click "Continue with Google"
3. Authorize
4. You're logged in! ✅

## 🔄 Google Login Flow

```
1. User clicks "Continue with Google"
   → Frontend calls: GET /api/v1/auth/google/url/
   → Gets Google OAuth URL

2. User redirects to Google
   → Logs in with Google account
   → Google redirects to: /auth/google/callback?code=...

3. Callback route handles OAuth
   → Extracts code from URL
   → Calls: POST /api/v1/auth/google/callback/
   → Receives JWT tokens + user data

4. Frontend stores tokens
   → Saves to localStorage
   → Updates auth store
   → Redirects to dashboard/profile

5. Subsequent API calls
   → Includes: Authorization: Bearer <token>
   → Auto-refreshes when expired
```

## 📦 Scripts

```bash
# Development
pnpm dev                # Dev server (localhost:5173)

# Production
pnpm build              # Build for production
pnpm start              # Start production server
pnpm preview            # Preview build

# Type Checking
pnpm check              # Run svelte-check
pnpm check:watch        # Watch mode

# Generate Types (Optional)
pnpm generate-types     # TypeScript from OpenAPI
```

## 🛠️ Development Workflow

Run both servers concurrently:

**Terminal 1:**
```bash
cd /home/ashwin/git-prjs/peeljobs/peeljobs
python manage.py runserver
# API: http://localhost:8000
```

**Terminal 2:**
```bash
cd /home/ashwin/git-prjs/peeljobs/peeljobs/ui
pnpm dev
# Frontend: http://localhost:5173
```

## 📚 Key Files

| File | Purpose |
|------|---------|
| `src/lib/api/auth.ts` | Auth API functions |
| `src/lib/stores/auth.ts` | Auth state management |
| `src/routes/login/+page.svelte` | Login page |
| `src/routes/auth/google/callback/+page.svelte` | OAuth callback |
| `src/lib/api/client.ts` | Base HTTP client |

## 🎨 Tech Stack

- **SvelteKit 2.x** - Modern framework
- **Svelte 5.x** - Reactive UI
- **TypeScript** - Type safety
- **Tailwind CSS 4.1** - Styling
- **Lucide Icons** - Beautiful icons
- **Vite** - Build tool

## 🔐 Auth Store Usage

```typescript
import { authStore } from '$lib/stores/auth';

// Subscribe to state
$: isAuthenticated = $authStore.isAuthenticated;
$: user = $authStore.user;

// Login
authStore.login(user, accessToken, refreshToken);

// Logout
authStore.logout();

// Refresh token
await authStore.refreshToken();
```

## 🚨 Troubleshooting

### "Failed to fetch" on login

**Cause:** Django not running
**Fix:** `python manage.py runserver`

### "redirect_uri_mismatch"

**Cause:** URI not in Google Console
**Fix:** Add `http://localhost:5173/auth/google/callback`

### API returns 401

**Cause:** Token expired
**Fix:** Should auto-refresh. If not, re-login.

### CORS errors

**Cause:** CORS not configured
**Fix:** Check `CORS_ALLOWED_ORIGINS` in Django includes `http://localhost:5173`

## 📖 Resources

- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Svelte 5 Docs](https://svelte.dev/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs/)
- [Django API Docs](../API_DOCUMENTATION.md)

## ✅ Setup Checklist

- [ ] `pnpm install`
- [ ] Django running on `localhost:8000`
- [ ] Google OAuth configured in Google Console
- [ ] `.env` has `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- [ ] `pnpm dev` starts successfully
- [ ] Visit `http://localhost:5173/login`
- [ ] Test Google login flow

## 🚀 Next Steps

1. Test Google login
2. Build dashboard components
3. Implement job search
4. Add profile management
5. Deploy to production

Happy coding! 🎉
