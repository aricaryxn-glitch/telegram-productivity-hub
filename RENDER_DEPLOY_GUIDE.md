# Render Deployment Guide

Follow this when the Render dashboard is open at the Blueprint repo-selection page.

## 1. Put the Code on GitHub

Render needs a GitHub, GitLab, or Bitbucket repo. This project is already a clean local Git repo and `.env` is ignored.

Create a new GitHub repo, then run these commands from this project folder:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-productivity-hub.git
git push -u origin main
```

If Git asks you to sign in, use your GitHub browser login or a GitHub personal access token.

## 2. Create the Render Blueprint

In Render:

1. Go to **New +**.
2. Choose **Blueprint**.
3. Select the GitHub repo you just pushed.
4. Blueprint path should be `render.yaml`.
5. Render should show:
   - `telegram-productivity-hub`
   - `telegram-productivity-hub-db`
6. Click **Apply** or **Deploy Blueprint**.

## 3. Add Required Environment Variables

When Render asks for values marked `sync: false`, paste:

```env
BOT_TOKEN=your Telegram bot token
ADMIN_IDS=@MORRISX3
FORCED_CHANNEL=https://t.me/MorrisXhub
GROQ_API_KEY=your Groq API key
```

Do not put quotes around the values.

## 4. Wait for Deploy

Open the web service logs. The app should build the Docker image, install Tesseract and Python packages, then start Uvicorn.

The health check should pass at:

```text
https://YOUR-RENDER-SERVICE.onrender.com/health
```

## 5. Confirm Telegram Webhook

The app automatically uses Render's `RENDER_EXTERNAL_URL` to set:

```text
https://YOUR-RENDER-SERVICE.onrender.com/telegram/webhook
```

After deploy, send `/start` to the Telegram bot.

## 6. Add Free Monitoring

Create a free UptimeRobot monitor:

- Type: HTTP(s)
- URL: `https://YOUR-RENDER-SERVICE.onrender.com/health`
- Interval: 5 minutes

This sends regular inbound traffic to the Render service and alerts you if it stops responding.

