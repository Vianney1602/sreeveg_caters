# 🚀 Quick Start Guide - User Authentication

## Get Started in 5 Minutes!

### Step 1: Install Dependencies (1 min)

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install PyJWT Flask-Mail
```

### Step 2: Create Environment Files (1 min)

**Frontend** - Create `frontend/.env`:

```env
REACT_APP_GOOGLE_CLIENT_ID=temporary-client-id
REACT_APP_API_URL=http://127.0.0.1:5000
```

**Backend** - Create `backend/.env`:

```env
SECRET_KEY=dev-secret-key-123
JWT_SECRET_KEY=jwt-secret-key-456
DATABASE_URL=your-existing-database-url
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Step 3: Start the Application (1 min)

**Terminal 1 - Backend:**

```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm start
```

### Step 4: Test Basic Flow (2 min)

1. Open http://localhost:3000
2. Click **"Continue as User"**
3. Click **"Create Account"**
4. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: test123
5. Click **"Create Account"**
6. You'll be redirected to the menu! 🎉

### Step 5: Set Up Google OAuth (Optional)

For Google sign-in to work:

1. Get Client ID from Google Cloud Console
   - See: `GOOGLE_OAUTH_QUICK_SETUP.md`
2. Update `REACT_APP_GOOGLE_CLIENT_ID` in `frontend/.env`
3. Restart frontend

## What You Get

✅ **User Registration** - Email + password signup
✅ **User Login** - Secure authentication
✅ **Google Sign-In** - One-click login
✅ **Password Reset** - OTP via email
✅ **Order History** - View past orders
✅ **Account Management** - Profile & settings
✅ **Beautiful UI** - Matches your theme

## Testing Features

### Test Registration

1. Welcome → Continue as User → Sign Up
2. Enter details → Create Account
3. ✅ Auto-logged in

### Test Login

1. Sign Out (from My Account)
2. Welcome → Continue as User → Sign In
3. Enter credentials → Sign In
4. ✅ Redirected to menu

### Test Password Reset

1. Sign In page → Forgot password?
2. Enter email → Send OTP
3. Check console for OTP (in dev mode)
4. Enter OTP → Enter new password
5. ✅ Password reset

### Test Order History

1. Sign in as user
2. Add items to cart → Checkout
3. Place order
4. Click "My Account" in header
5. Click "View Order History"
6. ✅ Order appears

## Styling

All pages match your home page design:

- 🎨 Deep red (#7a0000) primary color
- 🎨 Gold (#f5c542) accents
- 🎨 Smooth animations
- 🎨 Professional layouts

## Need Help?

- 📖 Full docs: `USER_AUTH_SETUP_GUIDE.md`
- 🔐 Google OAuth: `GOOGLE_OAUTH_QUICK_SETUP.md`
- 📝 Summary: `USER_AUTH_SUMMARY.md`

## Quick Commands

```bash
# Install frontend packages
cd frontend && npm install

# Install backend packages
cd backend && pip install -r requirements.txt

# Start backend
cd backend && python app.py

# Start frontend
cd frontend && npm start

# View errors
# Check browser console (F12)
# Check terminal for backend errors
```

## Common Issues

**"Cannot find module"** → Run `npm install` in frontend

**Google button not showing** → Add Client ID to .env and restart

**OTP not sending** → Email config needed (see setup guide)

**Orders not linking** → Check user token in sessionStorage

## Production Setup

When ready to deploy:

1. Generate strong JWT_SECRET_KEY
2. Set up production Google OAuth
3. Configure email service (SendGrid/SES)
4. Update CORS_ALLOWED_ORIGINS
5. Enable HTTPS

See `USER_AUTH_SETUP_GUIDE.md` for details.

---

**Ready to go!** 🚀
Start the servers and test the flow!
