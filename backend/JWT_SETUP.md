# JWT Setup Guide

## Overview

This application uses **Flask-JWT-Extended** for token-based authentication. JWT tokens are used to:

- Authenticate admin users
- Authenticate customer users
- Secure API endpoints
- Authenticate WebSocket connections

## Quick Setup

### 1. Generate JWT Secrets

Run the setup script to generate secure secrets automatically:

```powershell
cd backend
python scripts/generate_secrets.py
```

This creates a `.env` file with:

- `JWT_SECRET_KEY` - Secret for signing JWT tokens
- `SECRET_KEY` - Flask session secret
- `ADMIN_PASSWORD` - Auto-generated admin password

### 2. Configure Admin Credentials

Edit `backend/.env` and change:

```env
ADMIN_USERNAME=admin@yourdomain.com   # Change to your email
ADMIN_PASSWORD=^@qf$Bse3UjHZHog       # Keep the generated password or change it
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start the Server

```powershell
python app.py
```

## Manual Secret Generation

If you prefer to generate secrets manually:

```powershell
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Flask secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add them to `.env`:

```env
SECRET_KEY=your_flask_secret_here
JWT_SECRET_KEY=your_jwt_secret_here
```

## JWT Configuration

### Token Settings (in config.py)

```python
JWT_ACCESS_TOKEN_EXPIRES = 7200  # 2 hours (in seconds)
JWT_TOKEN_LOCATION = ["headers"]
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
```

### Adjusting Token Expiration

Edit `.env` to change expiration time:

```env
JWT_ACCESS_TOKEN_EXPIRES=3600    # 1 hour
JWT_ACCESS_TOKEN_EXPIRES=7200    # 2 hours
JWT_ACCESS_TOKEN_EXPIRES=86400   # 24 hours
```

## JWT Implementation Details

### Backend Endpoints

#### Admin Authentication

- **POST** `/api/admin/login` - Get access token

  ```json
  {
    "username": "admin@yourdomain.com",
    "password": "your_password"
  }
  ```

  Returns: `{"access_token": "...", "admin": {...}}`

- **GET** `/api/admin/verify` - Verify token validity (requires JWT)
- **POST** `/api/admin/refresh` - Refresh token before expiration (requires JWT)

#### Customer Authentication

- **POST** `/api/customers/register` - Register and get token
- **POST** `/api/customers/login` - Login and get token
- **POST** `/api/customers/refresh` - Refresh token (requires JWT)

#### Protected Endpoints (Require JWT)

- **GET** `/api/orders` - List all orders (Admin only)
- **PUT** `/api/orders/status/<id>` - Update order status (Admin only)
- **GET** `/api/customers` - List customers (Admin only)
- **GET** `/api/customers/<id>/orders` - Get customer orders (Customer only, must match token)
- **GET** `/api/admin/stats` - Admin statistics (Admin only)

### Frontend Implementation

#### Storing Tokens

Tokens are stored in localStorage:

```javascript
localStorage.setItem("adminToken", token); // Admin tokens
localStorage.setItem("customerToken", token); // Customer tokens
```

#### Sending Tokens

Axios interceptor automatically adds Authorization header:

```javascript
axios.interceptors.request.use((config) => {
  const token = authService.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### Token Refresh

```javascript
// Refresh token before it expires
await authService.refreshToken();
```

#### Auto-Logout on 401

Response interceptor handles expired tokens:

```javascript
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);
```

### WebSocket Authentication

WebSocket connections are authenticated with JWT:

```javascript
// Frontend - Pass token on connect
socketService.connect(token);

// Backend - Token is verified
// Invalid/expired tokens disconnect the client
```

## Identity Format

All JWT tokens now use **dict identity** format for consistency:

### Admin Token Identity

```python
{
    "admin_id": 1,
    "username": "admin@yourdomain.com",
    "email": "admin@yourdomain.com",
    "role": "Admin"
}
```

### Customer Token Identity

```python
{
    "customer_id": 123,
    "email": "customer@example.com"
}
```

## Security Best Practices

1. **Never commit `.env` to git** - It's in `.gitignore`
2. **Use strong secrets** - Run `generate_secrets.py` to create cryptographically secure secrets
3. **Change default admin credentials** - Update ADMIN_USERNAME and ADMIN_PASSWORD in `.env`
4. **Use HTTPS in production** - JWT tokens should only be sent over HTTPS
5. **Set appropriate token expiration** - Balance security vs user experience (default: 2 hours)
6. **Implement token refresh** - Use `/refresh` endpoints to renew tokens before expiration
7. **Validate tokens on WebSocket** - The server now disconnects invalid tokens

## Testing JWT

### Using cURL

```powershell
# Login
curl -X POST http://localhost:5000/api/admin/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin@yourdomain.com","password":"your_password"}'

# Use token in protected endpoint
curl http://localhost:5000/api/orders `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Refresh token
curl -X POST http://localhost:5000/api/admin/refresh `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using REST Client

See `frontend/src/services/requests.rest` for pre-configured requests.

## Troubleshooting

### "Invalid credentials" error

- Check ADMIN_USERNAME and ADMIN_PASSWORD in `.env`
- Ensure `.env` is loaded (run `generate_secrets.py` if missing)

### "Token expired" error

- Token has expired (default: 2 hours)
- Login again or use `/refresh` endpoint

### "Forbidden" error

- Token is valid but user doesn't have permission
- Admin endpoints require `role: "Admin"` in token
- Customer endpoints check customer_id matches

### WebSocket not connecting

- Check if token is being passed in `auth: {token}`
- Verify token is valid (not expired)
- Check browser console for connection errors

## Environment Variables Reference

```env
# Flask Configuration
SECRET_KEY=your_flask_secret          # Flask session secret

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret        # JWT signing secret (REQUIRED)
JWT_ACCESS_TOKEN_EXPIRES=7200         # Token lifetime in seconds (default: 2 hours)

# Admin Credentials
ADMIN_USERNAME=admin@yourdomain.com   # Admin login username
ADMIN_PASSWORD=your_secure_password   # Admin login password

# Database (optional)
SQLALCHEMY_DATABASE_URI=sqlite:///database.db

# Razorpay (optional - for payments)
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
```

## Files Modified for JWT Setup

### Backend

- `backend/config.py` - JWT configuration and .env loading
- `backend/app.py` - JWT manager initialization, WebSocket auth
- `backend/api/admin.py` - Admin login, verify, refresh endpoints
- `backend/api/customers.py` - Customer auth and refresh endpoints
- `backend/api/orders.py` - Protected order endpoints
- `backend/scripts/generate_secrets.py` - Secret generation script
- `backend/.env` - Environment variables (not in git)
- `backend/.env.example` - Template for environment variables

### Frontend

- `frontend/src/services/authService.js` - Token storage, axios interceptors, refresh
- `frontend/src/services/socketService.js` - WebSocket token passing
- `frontend/src/AccountPage.js` - Customer token usage
- `frontend/src/CartPage.js` - Optional token in orders
- `frontend/src/AdminDashboard.js` - Admin token verification

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review `frontend/src/services/requests.rest` for API examples
3. Check server logs for detailed error messages
