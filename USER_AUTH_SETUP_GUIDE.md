# User Authentication System - Complete Setup Guide

## Overview

This guide covers the complete implementation of user authentication, Google OAuth, password reset via OTP, and order history tracking for the Hotel Shanmuga Bhavaan catering website.

## Features Implemented

### 1. User Registration & Login

- Email/password-based registration
- Secure password hashing using Werkzeug
- JWT-based authentication
- Session persistence across page reloads
- Auto-login after successful registration

### 2. Google OAuth Integration

- Sign up with Google
- Sign in with Google
- Automatic user creation for new Google users
- Seamless integration with existing authentication flow

### 3. Password Management

- Forgot password functionality
- OTP-based password reset via email
- Change password from account settings
- OTP verification for password changes
- 10-minute OTP expiration

### 4. Order History

- View all past orders
- Order details including items, dates, and status
- Real-time order status updates
- Order tracking by user account

### 5. User Account Management

- View profile information
- Access order history
- Change password
- Logout functionality

## Files Created/Modified

### Frontend Files

#### New Components:

1. **UserSignUp.js** - User registration page with Google OAuth
2. **UserSignIn.js** - User login page with password reset
3. **OrderHistory.js** - Display user's order history
4. **UserAccount.js** - User profile and account management

#### Modified Files:

1. **App.js** - Added user authentication state and navigation
2. **WelcomePage.js** - Updated to navigate to user sign-up
3. **CartPage.js** - Modified to send user token with orders
4. **home.css** - Added authentication and account page styles
5. **index.js** - Wrapped app with GoogleOAuthProvider
6. **package.json** - Added dependencies

### Backend Files

#### New API Endpoints:

1. **api/users.py** - Complete user authentication API
   - POST /api/users/register - User registration
   - POST /api/users/login - User login
   - POST /api/users/google-login - Google OAuth login
   - POST /api/users/forgot-password - Send OTP
   - POST /api/users/verify-otp - Verify OTP
   - POST /api/users/reset-password - Reset password
   - POST /api/users/change-password - Change password
   - GET /api/users/order-history - Get user orders
   - GET /api/users/profile - Get user profile
   - PUT /api/users/profile - Update user profile

#### Modified Files:

1. **app.py** - Registered users blueprint
2. **api/orders.py** - Added user token support for order linking
3. **requirements.txt** - Added PyJWT and Flask-Mail

## Environment Variables Setup

### Frontend (.env in /frontend)

```env
REACT_APP_GOOGLE_CLIENT_ID=your-google-oauth-client-id
REACT_APP_API_URL=http://127.0.0.1:5000
```

### Backend (.env in /backend)

```env
JWT_SECRET_KEY=your-secret-jwt-key-change-in-production
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API

### Step 2: Create OAuth 2.0 Credentials

1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application"
4. Add authorized JavaScript origins:
   - http://localhost:3000
   - http://127.0.0.1:3000
   - Your production domain
5. Add authorized redirect URIs:
   - http://localhost:3000
   - Your production domain
6. Copy the Client ID

### Step 3: Configure Frontend

Add the Client ID to your frontend `.env`:

```env
REACT_APP_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

## Email Configuration for OTP

### Using Gmail

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account Settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. Add to backend `.env`:

```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
```

### Email Service Integration (Production)

For production, consider using:

- SendGrid
- Amazon SES
- Mailgun
- Postmark

Update `api/users.py` to integrate your chosen service.

## Installation & Setup

### Frontend Setup

```bash
cd frontend
npm install
# Packages installed: @react-oauth/google, jwt-decode
npm start
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
# New packages: PyJWT, Flask-Mail
python app.py
```

## Database Schema

The existing `customers` table already supports authentication:

```sql
customers (
  customer_id SERIAL PRIMARY KEY,
  full_name VARCHAR(100),
  phone_number VARCHAR(20),
  email VARCHAR(100),
  password_hash VARCHAR(255),  -- Used for password storage
  created_at TIMESTAMP,
  total_orders_count INTEGER
)
```

No database migration needed - uses existing schema.

## User Flow

### Registration Flow

1. User clicks "Continue as User" on welcome page
2. Redirected to sign-up page
3. Options:
   - Create account with email/password
   - Sign up with Google
4. After successful registration, redirected to menu page
5. User can now place orders linked to their account

### Login Flow

1. User navigates to sign-in page
2. Options:
   - Login with email/password
   - Sign in with Google
3. After login, redirected to menu page
4. Access to order history and account management

### Password Reset Flow

1. Click "Forgot password?" on sign-in page
2. Enter email address
3. Receive OTP via email
4. Enter OTP to verify
5. Set new password
6. Login with new credentials

### Order Placement

1. Logged-in users add items to cart
2. Checkout includes user authentication token
3. Orders automatically linked to user account
4. View orders in order history

## Security Features

### Password Security

- Passwords hashed using Werkzeug's security functions
- No plain-text password storage
- Minimum 6-character password requirement

### JWT Tokens

- 7-day token expiration
- Secure token storage in sessionStorage
- Token verification on protected routes

### OTP Security

- 6-digit random OTP generation
- 10-minute expiration time
- One-time use (deleted after successful verification)

### CORS Protection

- Configured allowed origins
- Credentials support enabled
- Secure headers

## Testing Guide

### Test User Registration

1. Navigate to welcome page
2. Click "Continue as User"
3. Fill registration form:
   - Name: Test User
   - Email: test@example.com
   - Phone: 1234567890
   - Password: test123
4. Click "Create Account"
5. Verify redirect to menu page

### Test Google Login

1. Click "Sign up with Google"
2. Select Google account
3. Verify account creation and redirect

### Test Password Reset

1. Go to sign-in page
2. Click "Forgot password?"
3. Enter registered email
4. Check console for OTP (or email in production)
5. Enter OTP
6. Set new password
7. Sign in with new password

### Test Order History

1. Sign in as user
2. Place an order
3. Click "My Account" in header
4. Click "View Order History"
5. Verify order appears in list

## Production Checklist

- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure production email service
- [ ] Set up Google OAuth for production domain
- [ ] Update CORS allowed origins
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Implement rate limiting on auth endpoints
- [ ] Add email verification for new registrations
- [ ] Set up monitoring and logging
- [ ] Test all auth flows end-to-end

## Troubleshooting

### Google OAuth Not Working

- Verify Client ID is correct in .env
- Check authorized origins include your domain
- Ensure GoogleOAuthProvider is wrapping App component
- Check browser console for errors

### OTP Not Sending

- Verify email credentials in .env
- Check mail server settings
- Enable "Less secure app access" or use app password
- Check spam folder

### Orders Not Linking to User

- Verify user token is being sent in headers
- Check token format: "Bearer <token>"
- Ensure orders API is extracting user_id from token
- Check customer_id is being set in order creation

### Session Not Persisting

- Verify token storage in sessionStorage
- Check token expiration (7 days)
- Ensure initialization logic checks for existing token

## API Documentation

### User Registration

```http
POST /api/users/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123",
  "phone": "1234567890"
}

Response 201:
{
  "message": "User registered successfully",
  "user_id": 123
}
```

### User Login

```http
POST /api/users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure123"
}

Response 200:
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890"
  }
}
```

### Order History

```http
GET /api/users/order-history
Authorization: Bearer <token>

Response 200:
{
  "orders": [
    {
      "order_id": 456,
      "customer_name": "John Doe",
      "event_type": "Delivery",
      "total_amount": 599.00,
      "status": "Completed",
      "created_at": "2026-01-13T10:30:00",
      "items": [...]
    }
  ]
}
```

## Support & Maintenance

For issues or questions:

1. Check browser console for errors
2. Check backend logs
3. Verify environment variables
4. Test API endpoints with Postman
5. Review this documentation

## Future Enhancements

Consider adding:

- Email verification on registration
- Social login (Facebook, Apple)
- Two-factor authentication
- Order notifications via email/SMS
- Loyalty points system
- Referral program
- Password strength meter
- Remember me option
- Profile picture upload
- Address book management
