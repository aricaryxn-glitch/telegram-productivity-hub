param(
    [string]$AppDir = "/opt/telegram-productivity-hub"
)

Write-Host "Upload this project to your VPS, create .env from .env.example, then run:"
Write-Host "docker compose up -d --build"
Write-Host "API health check: curl http://YOUR_SERVER:8000/health"
Write-Host "Bot process: docker compose exec app python -m app.bot"

