# Google OAuth Setup - Step by Step Guide

This is a detailed, step-by-step guide to set up Google OAuth for Panra.

## Prerequisites
- A Google account (Gmail account works)
- Access to Google Cloud Console

---

## Step 1: Create or Select a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown at the top (next to "Google Cloud")
4. Either:
   - **Select an existing project** (if you have one)
   - **Click "New Project"** to create a new one
     - Project name: `Panra` (or any name you prefer)
     - Click "Create"
     - Wait for the project to be created (takes a few seconds)

---

## Step 2: Configure OAuth Consent Screen

1. In the left sidebar, go to **"APIs & Services"** > **"OAuth consent screen"**
2. You'll see a form. Fill it out:

   **User Type:**
   - Select **"External"** (unless you have a Google Workspace account)
   - Click "Create"

   **App Information:**
   - **App name**: `Panra` (or your app name)
   - **User support email**: Your email address
   - **App logo**: (Optional - you can skip this)
   - **App domain**: (Optional - you can skip this)
   - **Application home page**: `https://panra-ke.up.railway.app` (your frontend URL)
   - **Privacy policy link**: (Optional for now)
   - **Terms of service link**: (Optional for now)
   - **Authorized domains**: (Optional - you can skip this)
   - Click "Save and Continue"

   **Scopes:**
   - Click "Add or Remove Scopes"
   - Check these scopes:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
   - Click "Update"
   - Click "Save and Continue"

   **Test Users** (if your app is in "Testing" mode):
   - Click "Add Users"
   - Add your Gmail address (and any other test emails)
   - Click "Add"
   - Click "Save and Continue"

   **Summary:**
   - Review the information
   - Click "Back to Dashboard"

---

## Step 3: Create OAuth 2.0 Credentials

1. In the left sidebar, go to **"APIs & Services"** > **"Credentials"**
2. Click the **"+ CREATE CREDENTIALS"** button at the top
3. Select **"OAuth client ID"**

   **Application type:**
   - Select **"Web application"**

   **Name:**
   - Enter: `Panra Web Client` (or any name)

   **Authorized JavaScript origins:**
   - Click "ADD URI"
   - Add these URLs (one at a time):
     ```
     http://localhost:3000
     https://panra-ke.up.railway.app
     ```
   - Note: These are your **frontend** URLs

   **Authorized redirect URIs:**
   - Click "ADD URI"
   - Add these URLs (one at a time):
     ```
     http://localhost:8001/accounts/google/login/callback/
     https://panra.up.railway.app/accounts/google/login/callback/
     ```
   - ⚠️ **IMPORTANT**: 
     - These are your **backend** URLs
     - Must include the trailing slash `/`
     - Must match exactly (including `https://` vs `http://`)

4. Click **"CREATE"**

5. **Copy your credentials:**
   - A popup will appear with:
     - **Your Client ID**: Something like `123456789-abc123def456.apps.googleusercontent.com`
     - **Your Client Secret**: Something like `GOCSPX-abc123def456`
   - ⚠️ **IMPORTANT**: Copy these NOW - you won't be able to see the secret again!
   - Click "OK"

---

## Step 4: Add Credentials to Railway (Production)

1. Go to your Railway dashboard
2. Select your **backend** service
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add these two variables:

   **Variable 1:**
   - **Key**: `GOOGLE_OAUTH_CLIENT_ID`
   - **Value**: Paste your Client ID (the one ending in `.apps.googleusercontent.com`)
   - Click "Add"

   **Variable 2:**
   - **Key**: `GOOGLE_OAUTH_CLIENT_SECRET`
   - **Value**: Paste your Client Secret (the one starting with `GOCSPX-`)
   - Click "Add"

6. Railway will automatically redeploy your backend with the new variables

---

## Step 5: Add Credentials for Local Development (Optional)

If you want to test locally:

1. In your `backend` directory, create or edit `.env` file:
   ```bash
   cd backend
   nano .env  # or use your preferred editor
   ```

2. Add these lines:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
   ```

3. Replace `your-client-id-here` and `your-client-secret-here` with your actual values

4. Save the file

---

## Step 6: Run Database Migrations

Django-allauth needs database tables. Run migrations:

```bash
cd backend
python manage.py migrate
```

This will create tables like:
- `socialaccount_socialaccount`
- `socialaccount_socialapp`
- `socialaccount_socialtoken`
- And other allauth tables

---

## Step 7: Test the Setup

1. **Restart your backend** (if it's running):
   - Railway will auto-restart after adding environment variables
   - For local: Stop and restart your Django server

2. **Go to your frontend** (login or signup page)

3. **Click "Continue with Google"**

4. **Expected flow:**
   - You should be redirected to Google's login page
   - After logging in, Google asks for permission
   - You should be redirected back to your app
   - You should be automatically logged in

---

## Troubleshooting

### Error: "Redirect URI mismatch"
- **Problem**: The redirect URI in Google Console doesn't match what your app is using
- **Fix**: 
  - Check the redirect URI in Google Console exactly matches:
    - `https://panra.up.railway.app/accounts/google/login/callback/`
  - Must include trailing slash
  - Must use `https://` (not `http://`) for production

### Error: "Invalid client"
- **Problem**: Client ID or Secret is wrong
- **Fix**:
  - Double-check environment variables in Railway
  - Make sure there are no extra spaces
  - Restart backend after adding variables

### Error: "Access blocked: This app's request is invalid"
- **Problem**: OAuth consent screen not configured or app is in testing mode
- **Fix**:
  - Make sure you completed Step 2 (OAuth consent screen)
  - If in testing mode, add your email as a test user
  - Or publish your app (requires verification for production)

### Error: Database table doesn't exist
- **Problem**: Migrations not run
- **Fix**: Run `python manage.py migrate`

### Error: "Module not found: allauth"
- **Problem**: django-allauth not installed
- **Fix**: Run `pip install -r requirements.txt`

---

## Quick Checklist

- [ ] Created/selected Google Cloud project
- [ ] Configured OAuth consent screen
- [ ] Created OAuth 2.0 credentials
- [ ] Added redirect URIs (with trailing slashes)
- [ ] Copied Client ID and Secret
- [ ] Added environment variables to Railway
- [ ] Ran database migrations
- [ ] Tested the login flow

---

## Security Notes

1. **Never commit** your Client Secret to Git
2. The `.env` file should be in `.gitignore`
3. Keep your Client Secret secure
4. If you accidentally expose it, regenerate it in Google Console

---

## Need Help?

If you encounter issues:
1. Check the Railway backend logs for errors
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Make sure redirect URIs match exactly (including trailing slashes)



