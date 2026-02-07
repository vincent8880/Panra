# Google OAuth Setup Guide

This guide explains how to set up Google OAuth authentication for Panra.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. Access to the Google Cloud Console

## Step 1: Create OAuth 2.0 Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** (or **Google Identity Services API**)
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" or "Google Identity Services API"
   - Click "Enable"

4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen first:
     - Choose "External" user type (unless you have a Google Workspace)
     - Fill in the required fields (App name, User support email, Developer contact)
     - Add scopes: `email` and `profile`
     - Add test users if your app is in testing mode
   - Application type: **Web application**
   - Name: "Panra Web Client" (or any name you prefer)
   - **Authorized JavaScript origins**:
     ```
     http://localhost:3000
     https://panra-ke.up.railway.app
     https://your-production-domain.com
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:8001/accounts/google/login/callback/
     https://panra.up.railway.app/accounts/google/login/callback/
     https://your-backend-domain.com/accounts/google/login/callback/
     ```
   - Click "Create"
   - **Copy the Client ID and Client Secret** - you'll need these for environment variables

## Step 2: Configure Environment Variables

### Backend (Railway)

Add these environment variables to your Railway backend service:

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
```

### Local Development

Add to your `.env` file in the backend directory:

```
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
```

## Step 3: Install Dependencies

The backend requires `django-allauth`. Install it:

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `django-allauth>=0.57.0`

## Step 4: Run Migrations

Django-allauth requires database tables. Run migrations:

```bash
cd backend
python manage.py migrate
```

This will create the necessary tables for social accounts.

## Step 5: Verify Setup

1. **Backend**: Make sure the backend is running and can access the Google OAuth credentials
2. **Frontend**: The login and signup pages should now show a "Continue with Google" button
3. **Test Flow**:
   - Click "Continue with Google" on the login/signup page
   - You should be redirected to Google's login page
   - After logging in, you should be redirected back to your app
   - You should be automatically logged in

## Troubleshooting

### "Redirect URI mismatch" error

- Make sure the redirect URI in Google Cloud Console exactly matches:
  - `https://your-backend-domain.com/accounts/google/login/callback/`
- The URI must include the protocol (`https://`), domain, and path
- No trailing slashes issues - make sure it matches exactly

### "Invalid client" error

- Verify `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are set correctly
- Make sure there are no extra spaces or quotes in the environment variables
- Restart the backend server after setting environment variables

### User not being created

- Check that `SOCIALACCOUNT_AUTO_SIGNUP = True` in `settings.py`
- Verify the user model allows the email/username being used
- Check backend logs for any errors during user creation

### CORS errors

- Make sure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Verify `FRONTEND_URL` is set correctly in backend settings
- Check that `CORS_ALLOW_CREDENTIALS = True` is set

## Security Notes

1. **Never commit** `GOOGLE_OAUTH_CLIENT_SECRET` to version control
2. Use different OAuth credentials for development and production
3. Regularly rotate your OAuth client secrets
4. Monitor OAuth usage in Google Cloud Console for suspicious activity

## Additional Configuration

### Customizing User Creation

The `CustomSocialAccountAdapter` in `backend/users/adapters.py` handles user creation. You can customize:
- Username generation
- Email handling
- Profile creation
- Initial credits assignment

### Email Verification

Currently, email verification is disabled (`ACCOUNT_EMAIL_VERIFICATION = 'none'`). To enable it:
1. Set `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` in `settings.py`
2. Configure email backend (SMTP settings)
3. Update the adapter to handle email verification flow

## Support

If you encounter issues:
1. Check backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test with a fresh OAuth client ID/secret
4. Ensure all URLs match exactly between Google Console and your app








