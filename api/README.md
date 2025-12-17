# PeelJobs API - Job Seeker Authentication

Modern REST API for PeelJobs Job Seeker authentication using Google OAuth 2.0 and JWT tokens.

## 🎯 Overview

This API provides stateless, token-based authentication for Job Seekers, designed for modern frontend frameworks (SvelteKit, Flutter, React, Vue, etc.).

### Features

- ✅ Google OAuth 2.0 integration
- ✅ JWT access tokens (1 hour) + refresh tokens (7 days)
- ✅ Automatic token rotation
- ✅ Token blacklisting on logout
- ✅ CORS enabled for frontend frameworks
- ✅ User profile management
- ✅ Comprehensive tests

## 📁 Structure

```
api/
├── __init__.py
├── apps.py
├── urls.py              # Main API routing
├── README.md            # This file
└── v1/
    ├── __init__.py
    ├── urls.py          # v1 API routing
    └── auth/
        ├── __init__.py
        ├── serializers.py   # Request/response serializers
        ├── views.py         # API endpoints
        ├── utils.py         # Helper functions
        ├── urls.py          # Auth routing
        └── tests.py         # Unit tests
```

## 🚀 Quick Start

### 1. Configure Google OAuth

Add to `.env`:
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_LOGIN_HOST=http://localhost:8000
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Start Server

```bash
python manage.py runserver
```

### 4. Test Endpoints

```bash
# Get Google OAuth URL
curl "http://localhost:8000/api/v1/auth/google/url/?redirect_uri=http://localhost:3000/callback"

# After getting code from Google
curl -X POST http://localhost:8000/api/v1/auth/google/callback/ \
  -H "Content-Type: application/json" \
  -d '{"code": "YOUR_CODE", "redirect_uri": "http://localhost:3000/callback"}'

# Get current user (with JWT token)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/v1/auth/me/
```

## 📡 Available Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/auth/google/url/` | Get Google OAuth URL | No |
| POST | `/api/v1/auth/google/callback/` | Exchange code for JWT tokens | No |
| GET | `/api/v1/auth/me/` | Get current user | Yes |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token | No |
| POST | `/api/v1/auth/token/verify/` | Verify token validity | No |
| POST | `/api/v1/auth/google/disconnect/` | Disconnect Google account | Yes |
| POST | `/api/v1/auth/logout/` | Logout (blacklist token) | No |

## 🔑 Authentication

Use JWT Bearer token in Authorization header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🧪 Testing

Run unit tests:

```bash
python manage.py test api.v1.auth.tests
```

Test coverage includes:
- Google OAuth URL generation
- Callback handling for new users
- Callback handling for existing users
- Token refresh
- User profile retrieval
- Google account disconnection
- Logout with token blacklisting

## 📖 Documentation

- **[API Documentation](../API_DOCUMENTATION.md)** - Complete API reference
- **[Quick Start Guide](../API_QUICKSTART.md)** - Frontend integration guide

## 🔧 Configuration

### JWT Settings (settings.py)

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}
```

### CORS Settings (settings.py)

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # SvelteKit
    "http://localhost:4200",  # Angular
    "http://localhost:5173",  # Vite
]
CORS_ALLOW_CREDENTIALS = True
```

## 🎨 Frontend Integration

### SvelteKit Example

```typescript
// Get Google OAuth URL
const response = await fetch(
  'http://localhost:8000/api/v1/auth/google/url/?redirect_uri=http://localhost:3000/callback'
);
const { auth_url } = await response.json();
window.location.href = auth_url;

// Handle callback
const response = await fetch('http://localhost:8000/api/v1/auth/google/callback/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ code: 'GOOGLE_CODE', redirect_uri: 'http://localhost:3000/callback' })
});
const { access, refresh, user } = await response.json();

// Use access token
const response = await fetch('http://localhost:8000/api/v1/auth/me/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
```

## 🔐 Security

- **HTTPS Only**: Always use HTTPS in production
- **Token Storage**: Store tokens securely (httpOnly cookies recommended)
- **Token Expiry**: Access tokens expire in 1 hour
- **Token Rotation**: Refresh tokens are rotated on each refresh
- **Blacklisting**: Old tokens are blacklisted after rotation
- **CORS**: Configure allowed origins in production

## 🚧 Future Enhancements

### Phase 2: Job APIs (Coming Soon)
- Job search and filtering
- Job applications
- Saved jobs
- Job recommendations

### Phase 3: Profile APIs (Coming Soon)
- Profile CRUD operations
- Resume upload and management
- Skills management
- Education and experience

### Phase 4: Additional Features
- Real-time notifications (WebSocket)
- Job alerts
- Application tracking
- Interview scheduling

## 📝 Migration Notes

### From Session-based Auth

Old flow (session-based):
```
User → /social/google_login/ → Google → Session cookie
```

New flow (JWT-based):
```
Frontend → GET /api/v1/auth/google/url/ → Google
Google → Frontend callback → POST /api/v1/auth/google/callback/ → JWT tokens
```

**Key Differences:**
- Stateless (no sessions)
- Frontend manages tokens
- Works with any client (web, mobile, desktop)
- Better for microservices architecture

## 🐛 Known Issues

None at this time.

## 🤝 Contributing

1. Write tests for new features
2. Follow Django REST Framework best practices
3. Update documentation
4. Run tests before committing: `python manage.py test api`

## 📞 Support

- Email: support@peeljobs.com
- GitHub Issues: https://github.com/micropyramid/peeljobs/issues

## 📄 License

Same as main PeelJobs project.

---

**Built with** ❤️ **for modern Job Seekers**
