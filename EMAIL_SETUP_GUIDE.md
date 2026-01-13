# Email Configuration Guide for OTP Functionality

## Issue

OTP emails are not being sent because email credentials are not configured in the `.env` file.

## Solution

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable it if not already enabled)
3. Scroll down to **App passwords**
4. Click **Select app** → Choose "Mail"
5. Click **Select device** → Choose "Other" and type "Hotel Shanmuga Bhavaan"
6. Click **Generate**
7. Copy the 16-character app password (it will look like: `abcd efgh ijkl mnop`)

### Step 2: Update Backend .env File

Open `backend/.env` and update these lines:

```dotenv
# Email Configuration for OTP (Optional - for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-actual-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password-here
MAIL_DEFAULT_SENDER=your-actual-email@gmail.com
```

**Example:**

```dotenv
MAIL_USERNAME=shanmugabhavaan@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_DEFAULT_SENDER=shanmugabhavaan@gmail.com
```

### Step 3: Update Render Environment Variables (Production)

If deploying to Render, add these environment variables in your backend service:

1. Go to Render Dashboard → Your Backend Service
2. Navigate to **Environment** tab
3. Add these variables:
   - `MAIL_USERNAME` = your-email@gmail.com
   - `MAIL_PASSWORD` = your-16-char-app-password
   - `MAIL_DEFAULT_SENDER` = your-email@gmail.com

### Step 4: Restart Backend Server

After updating `.env`:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
python app.py
```

## How It Works Now

1. **Email Configured**: OTP will be sent via email with professional HTML formatting
2. **Email Not Configured**: OTP will be printed to server console as fallback

## Testing

1. Go to User Sign In page
2. Click "Forgot Password?"
3. Enter your email
4. You should receive an email with:
   - Subject: "Your OTP for Password Reset - Hotel Shanmuga Bhavaan"
   - Professional HTML template with OTP code
   - Valid for 10 minutes

## Alternative Email Providers

### Using Other Email Services

**SendGrid:**

```dotenv
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

**Outlook/Hotmail:**

```dotenv
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

**Custom SMTP:**

```dotenv
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
```

## Troubleshooting

### Error: "Email not configured"

- Check that `MAIL_USERNAME` and `MAIL_PASSWORD` are set in `.env`
- Restart the backend server after changing `.env`

### Error: "Authentication failed"

- Make sure you're using an App Password, not your regular Gmail password
- Check that 2-Step Verification is enabled on your Google account

### Email not received

- Check spam/junk folder
- Verify the email address is correct
- Check server console for error messages
- Test with a different email provider

### Gmail blocks the email

- Make sure "Less secure app access" is OFF (use App Passwords instead)
- Check Google Account security settings for any blocks

## Security Notes

- **Never commit `.env` file to Git** (it's already in `.gitignore`)
- Use App Passwords, not your main account password
- Rotate App Passwords periodically
- For production, consider using professional email services like SendGrid or AWS SES

## Code Changes Made

1. ✅ Added Flask-Mail to `extensions.py`
2. ✅ Initialized Flask-Mail in `app.py`
3. ✅ Added email configuration to `config.py`
4. ✅ Implemented `send_otp_email()` function with HTML template
5. ✅ Updated `/forgot-password` endpoint to send actual emails
6. ✅ Added fallback to console printing if email is not configured

## Features

- Professional HTML email template with Hotel Shanmuga Bhavaan branding
- OTP displayed in large, easy-to-read format
- 10-minute expiration notice
- Plain text fallback for email clients that don't support HTML
- Graceful fallback to console if email is not configured
