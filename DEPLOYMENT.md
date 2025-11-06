# Deployment Guide

This guide will help you deploy your Flask app to a hosting platform with automatic deployment from GitHub.

## Prerequisites
- GitHub account
- Git installed on your computer

## Step 1: Push to GitHub

1. Initialize Git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a new repository on GitHub (https://github.com/new)

3. Link and push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Choose a Hosting Platform

### Option A: Render (Recommended - Free tier available)

1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: Your app name
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

5. Add Environment Variables:
   - Go to "Environment" tab
   - Add these variables:
     - `SECRET_KEY` = (generate a random secret key)
     - `GEMINI_API_KEY` = `AIzaSyDZR88mTYQTgK2TwE13dFdWR29QQG8Wnn0`
     - `PYTHON_VERSION` = `3.11.0`

6. Click "Create Web Service"

**Note**: Selenium/Chrome may not work on Render's free tier. Consider upgrading or using a different platform for ERP scraping features.

### Option B: Railway (Free tier with GitHub integration)

1. Go to https://railway.app and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect it's a Flask app
5. Add Environment Variables in the "Variables" tab:
   - `SECRET_KEY` = (generate a random secret key)
   - `GEMINI_API_KEY` = `AIzaSyDZR88mTYQTgK2TwE13dFdWR29QQG8Wnn0`

6. Deploy automatically starts

### Option C: PythonAnywhere (For Selenium support)

1. Sign up at https://www.pythonanywhere.com
2. Go to "Web" tab → "Add a new web app"
3. Choose Flask and Python 3.11
4. Upload your files or use Git to clone your repo
5. Configure WSGI file to point to your app
6. Install Chrome/ChromeDriver for Selenium features
7. Set environment variables in WSGI configuration

## Step 3: Configure Automatic Deployments

### For Render:
- Automatic deployments are enabled by default
- Every push to `main` branch triggers a new deployment

### For Railway:
- Automatic deployments are enabled by default
- Every push triggers a rebuild

### For PythonAnywhere:
- Set up a post-receive Git hook or use their API
- Or manually pull changes and reload

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | No (for AI features) |
| `PORT` | Port to run on | No (auto-set by platform) |

## Important Notes

1. **Security**: Never commit your `.env` file or hardcoded API keys to GitHub
2. **Selenium**: Chrome/ChromeDriver may not work on free tiers. Consider:
   - Using a paid tier
   - Using Selenium Grid
   - Disabling ERP scraping features for deployment
3. **File uploads**: Most free platforms have ephemeral storage. Uploaded files will be deleted on restart.
4. **Database**: If you add a database later, use the platform's database service

## Testing Your Deployment

After deployment, test:
1. Homepage loads correctly
2. File upload functionality works
3. All routes are accessible
4. Check logs for any errors

## Troubleshooting

### App doesn't start
- Check logs in your hosting platform dashboard
- Verify all dependencies in `requirements.txt` are compatible
- Ensure PORT is configured correctly

### Selenium errors
- Selenium requires Chrome/ChromeDriver which may not be available on free tiers
- Consider commenting out Selenium-dependent features for deployment

### File upload issues
- Check if your platform supports persistent storage
- Consider using cloud storage (AWS S3, Cloudinary, etc.)

## Auto-Deploy Workflow

Once set up:
1. Make changes to your code locally
2. Commit: `git commit -am "Your message"`
3. Push: `git push origin main`
4. Platform automatically detects changes and redeploys
5. Your app will be live in 1-3 minutes

## Support

For platform-specific issues, check:
- Render: https://render.com/docs
- Railway: https://docs.railway.app
- PythonAnywhere: https://help.pythonanywhere.com
