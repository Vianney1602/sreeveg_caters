# Quick Start - Google OAuth Setup

## 1. Get Google OAuth Client ID

### Step-by-Step:

1. **Go to Google Cloud Console**

   - Visit: https://console.cloud.google.com/

2. **Create or Select Project**

   - Click "Select a project" at the top
   - Click "New Project"
   - Name it "Hotel Shanmuga Bhavaan" or similar
   - Click "Create"

3. **Enable Google OAuth API**

   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Configure OAuth Consent Screen**

   - Go to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Click "Create"
   - Fill in required fields:
     - App name: Hotel Shanmuga Bhavaan
     - User support email: your-email@gmail.com
     - Developer contact: your-email@gmail.com
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add test users if needed
   - Click "Save and Continue"

5. **Create OAuth 2.0 Credentials**

   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"
   - Application type: "Web application"
   - Name: "Shanmuga Bhavaan Web Client"
   - Authorized JavaScript origins:
     ```
     http://localhost:3000
     http://127.0.0.1:3000
     ```
   - Click "Create"
   - **COPY THE CLIENT ID** - it looks like:
     ```
     123456789012-abc123xyz789.apps.googleusercontent.com
     ```

6. **Add Client ID to Frontend**

   - Create/edit `frontend/.env`:
     ```env
     REACT_APP_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
     ```
   - Replace `your-client-id-here` with your actual Client ID

7. **Restart Frontend**
   ```bash
   cd frontend
   npm start
   ```

## 2. Test Google Login

1. Start both backend and frontend
2. Navigate to welcome page
3. Click "Continue as User"
4. Click "Sign up with Google" button
5. Select your Google account
6. Grant permissions
7. You should be logged in and redirected to menu page

## Production Setup

When deploying to production:

1. Go back to Google Cloud Console > Credentials
2. Edit your OAuth client ID
3. Add your production domain to:
   - Authorized JavaScript origins:
     ```
     https://yourdomain.com
     ```
   - Authorized redirect URIs:
     ```
     https://yourdomain.com
     ```
4. Update production `.env` with same Client ID

## Troubleshooting

### "redirect_uri_mismatch" Error

- Make sure your authorized origins include the exact URL you're testing from
- Check for http vs https
- Restart your app after changing .env

### Google Button Not Appearing

- Check browser console for errors
- Verify Client ID is correct in .env
- Ensure @react-oauth/google package is installed
- Check that GoogleOAuthProvider wraps your App component

### "popup_closed_by_user" Error

- This is normal - user closed the popup
- Not an error, just means they cancelled

### Token Not Working

- Token is automatically handled
- Check sessionStorage for '\_userToken' and '\_user'
- Verify backend is receiving Authorization header

## Need Help?

- Google OAuth Docs: https://developers.google.com/identity/protocols/oauth2
- React OAuth Library: https://www.npmjs.com/package/@react-oauth/google
- Check USER_AUTH_SETUP_GUIDE.md for full documentation
