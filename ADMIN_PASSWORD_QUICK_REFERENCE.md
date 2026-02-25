# ADMIN PASSWORD MANAGEMENT - QUICK REFERENCE GUIDE

**For:** Hotel Shanmuga Bhavaan Admin  
**Date:** February 25, 2026  
**Version:** 1.0

---

## 🔐 TWO WAYS TO CHANGE YOUR PASSWORD

### METHOD 1: If You Forgot Your Password ❌

**Step 1: Request OTP**
```
Endpoint: POST /api/users/admin/forgot-password
URL: https://api.hotelshanmugabhavaan.com/api/users/admin/forgot-password
Method: POST
Auth Required: NO

Request Body:
{
  "email": "hotelshanmugabhavaan@gmail.com"
}

Example using curl:
curl -X POST https://api.hotelshanmugabhavaan.com/api/users/admin/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"hotelshanmugabhavaan@gmail.com"}'

Expected Response:
{
  "message": "OTP sent to admin email"
}
```

**Step 2: Check Email for OTP**
- You will receive an email with your 6-digit OTP code
- Valid for 10 minutes
- Example: 123456

**Step 3: Verify OTP**
```
Endpoint: POST /api/users/admin/verify-otp
URL: https://api.hotelshanmugabhavaan.com/api/users/admin/verify-otp
Method: POST
Auth Required: NO

Request Body:
{
  "otp": "123456"
}

Example using curl:
curl -X POST https://api.hotelshanmugabhavaan.com/api/users/admin/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"otp":"123456"}'

Expected Response:
{
  "message": "Admin OTP verified successfully"
}
```

**Step 4: Reset Password with OTP**
```
Endpoint: POST /api/users/admin/reset-password
URL: https://api.hotelshanmugabhavaan.com/api/users/admin/reset-password
Method: POST
Auth Required: NO

Request Body:
{
  "otp": "123456",
  "new_password": "YourNewPassword@123"
}

Example using curl:
curl -X POST https://api.hotelshanmugabhavaan.com/api/users/admin/reset-password \
  -H "Content-Type: application/json" \
  -d '{"otp":"123456","new_password":"YourNewPassword@123"}'

Expected Response:
{
  "message": "Admin password reset successfully"
}
```

**Step 5: Login with New Password**
```
Endpoint: POST /api/users/login
URL: https://api.hotelshanmugabhavaan.com/api/users/login
Method: POST
Auth Required: NO

Request Body:
{
  "email": "hotelshanmugabhavaan@gmail.com",
  "password": "YourNewPassword@123"
}

Example using curl:
curl -X POST https://api.hotelshanmugabhavaan.com/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"hotelshanmugabhavaan@gmail.com","password":"YourNewPassword@123"}'

Expected Response:
{
  "message": "Login successful",
  "token": "JWT_TOKEN_HERE",
  "isAdmin": true,
  "user": {
    "id": 1,
    "name": "Admin",
    "email": "hotelshanmugabhavaan@gmail.com",
    "role": "Admin"
  }
}

✅ You are now logged in!
Save the JWT token for authenticated requests.
```

---

### METHOD 2: Change Password While Logged In ✅

**Prerequisites:**
- You are already logged in
- You have a valid JWT token
- You know your current password

**Step 1: Change Password**
```
Endpoint: POST /api/users/admin/change-password
URL: https://api.hotelshanmugabhavaan.com/api/users/admin/change-password
Method: POST
Auth Required: YES

Request Headers:
{
  "Authorization": "Bearer {JWT_TOKEN}",
  "Content-Type": "application/json"
}

Request Body:
{
  "current_password": "YourCurrentPassword@123",
  "new_password": "YourNewPassword@456"
}

Example using curl:
curl -X POST https://api.hotelshanmugabhavaan.com/api/users/admin/change-password \
  -H "Authorization: Bearer JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"YourCurrentPassword@123","new_password":"YourNewPassword@456"}'

Expected Response:
{
  "message": "Admin password changed successfully"
}
```

**Step 2: Optional - Login Again**
- If you want to continue using the dashboard, you may need to logout and login again
- Use your new password to login

---

## 🔑 PASSWORD REQUIREMENTS

Your admin password should:
- ✅ Be at least 8 characters long
- ✅ Contain uppercase letters (A-Z)
- ✅ Contain lowercase letters (a-z)
- ✅ Contain numbers (0-9)
- ✅ Contain special characters (@, #, $, %, etc.)

**Example of Strong Password:**
- ✅ Admin@123Secure
- ✅ MyHotel#2026Password
- ✅ Shanmuga$Bhavaan123

---

## ⚠️ COMMON ERRORS & SOLUTIONS

### Error: "OTP is required"
**Problem:** You didn't include OTP in the request  
**Solution:** Make sure your request body includes `"otp": "123456"`

```json
{
  "otp": "123456",
  "new_password": "YourNewPassword@123"
}
```

---

### Error: "Invalid OTP format"
**Problem:** OTP is not exactly 6 digits  
**Solution:** Make sure OTP is 6 numbers: 123456

---

### Error: "OTP not found or expired"
**Problem:** OTP has expired (valid for only 10 minutes)  
**Solution:** Request a new OTP by calling forgot-password endpoint again

---

### Error: "Invalid OTP"
**Problem:** OTP code is incorrect  
**Solution:** Check your email again and enter the correct OTP code

---

### Error: "Authorization token required"
**Problem:** You didn't include JWT token in Authorization header  
**Solution:** Include the header: `Authorization: Bearer YOUR_JWT_TOKEN_HERE`

```bash
curl -X POST https://api.hotelshanmugabhavaan.com/api/users/admin/change-password \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"OldPassword@123","new_password":"NewPassword@456"}'
```

---

### Error: "Current password is incorrect"
**Problem:** The password you entered doesn't match the stored password  
**Solution:** Make sure you're entering your current admin password correctly

---

### Error: "Admin access required"
**Problem:** Your JWT token doesn't have admin role  
**Solution:** Use the JWT token obtained by logging in with admin credentials

---

## 📧 EMAIL CONFIGURATION

### If You Don't Receive OTP Email:

1. **Check Spam Folder**
   - OTP emails may go to spam/junk
   - Add admin@email to your contacts

2. **Verify Email Address**
   - Make sure email is: hotelshanmugabhavaan@gmail.com
   - Check for typos

3. **Contact Support**
   - If email service is not configured
   - Check application logs for email errors

---

## 🔒 SECURITY TIPS

### 1. Strong Password
- Use mix of uppercase, lowercase, numbers, special characters
- At least 12 characters is recommended
- Don't use dictionary words

### 2. OTP Safety
- Never share your OTP with anyone
- OTP valid for only 10 minutes
- Single-use only (automatically cleared after use)

### 3. JWT Token
- Keep your JWT token secret
- Don't share the token in URLs or unencrypted messages
- Token expires after 7 days

### 4. Password Changes
- Change your password periodically
- Never write password on sticky notes
- Store passwords in secure password manager

---

## 📱 USING WITH POSTMAN

### 1. Import Collection
```
Import Postman_Cater_Local.postman_collection.json from project root
```

### 2. Set Environment Variables
```
Environment: Postman_Cater_Local.postman_environment.json
Variables:
  - base_url: https://api.hotelshanmugabhavaan.com
  - admin_email: hotelshanmugabhavaan@gmail.com
  - jwt_token: (set after login)
```

### 3. Test Forgot-Password Flow

**Request 1: Forgot Password**
```
POST {{base_url}}/api/users/admin/forgot-password
Body (raw JSON):
{
  "email": "{{admin_email}}"
}
```

**Request 2: Verify OTP**
```
POST {{base_url}}/api/users/admin/verify-otp
Body (raw JSON):
{
  "otp": "123456"  # Replace with OTP from email/console
}
```

**Request 3: Reset Password**
```
POST {{base_url}}/api/users/admin/reset-password
Body (raw JSON):
{
  "otp": "123456",
  "new_password": "YourNewPassword@456"
}
```

### 4. Test Change-Password Flow

**Request 1: Get JWT Token**
```
POST {{base_url}}/api/users/login
Body (raw JSON):
{
  "email": "{{admin_email}}",
  "password": "CurrentPassword@123"
}
Response: Save the token to {{jwt_token}}
```

**Request 2: Change Password**
```
POST {{base_url}}/api/users/admin/change-password
Headers:
  Authorization: Bearer {{jwt_token}}
Body (raw JSON):
{
  "current_password": "CurrentPassword@123",
  "new_password": "NewPassword@456"
}
```

---

## 🛠️ DEVELOPER INFORMATION

### Endpoint Locations
- **File:** backend/api/users.py
- **Routes:** Lines 486-720
- **Model:** backend/models.py (AdminSettings, lines 135-146)

### Router Details
```
Endpoint Route         | Method | Auth | Purpose
-----------------------+--------+------+------------------
/api/users/forgot-password | POST | NO   | Request OTP
/api/users/verify-otp    | POST | NO   | Verify OTP
/api/users/reset-password | POST | NO   | Reset password
/api/users/change-password | POST | YES  | Change password
/api/users/login        | POST | NO   | Login (enhanced)
```

### Database Table
```
Table: admin_settings
Columns:
  - id (Integer, Primary Key)
  - admin_id (Integer, default=1)
  - password_hash (String, hashed with werkzeug)
  - email (String)
  - updated_at (DateTime, auto-updates)
```

### Storage Mechanism
```
Primary: Redis
  - Key: otp:admin:{email}
  - TTL: 600 seconds (10 minutes)

Fallback: In-Memory Dictionary
  - Key: admin:{email}
  - Value: {otp, expires}
```

---

## 📞 SUPPORT CONTACT

**For Issues:**
1. Email: hotelshanmugabhavaan@gmail.com
2. Check server logs: `journalctl -u cater-backend -f`
3. Review documentation in project root

**Documentation Files:**
- ADMIN_PASSWORD_ENDPOINTS_VERIFICATION.md
- ADMIN_ENDPOINTS_IMPLEMENTATION_SUMMARY.md
- DETAILED_CODE_CHANGES_BEFORE_AFTER.md

---

## ✅ CHECKLIST

Before attempting password change:
- [ ] I know my current/old password
- [ ] I have a strong new password ready
- [ ] I have internet connection
- [ ] I can access my email
- [ ] I understand password requirements

---

**Last Updated:** February 25, 2026  
**Version:** 1.0  
**Status:** ✅ COMPLETE

