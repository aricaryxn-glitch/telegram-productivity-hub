# UptimeRobot Monitor

Render Free web services spin down after 15 minutes without inbound traffic. A free UptimeRobot HTTP monitor can check the app every 5 minutes.

Create one monitor:

- Monitor Type: `HTTP(s)`
- Friendly Name: `Telegram Productivity Hub`
- URL: `https://YOUR-RENDER-SERVICE.onrender.com/health`
- Monitoring Interval: `5 minutes`

Use the same `/health` URL as the Render health check. This keeps the service receiving inbound traffic and also alerts you if the API stops responding.

Notes:

- Replace `YOUR-RENDER-SERVICE` after Render gives you the actual URL.
- Keeping one Render Free web service awake all month uses roughly 720 of the 750 included free instance hours.
- Render can still restart or suspend free services under its documented free-tier limits.

