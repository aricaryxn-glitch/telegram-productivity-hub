# Telegram Productivity & Document Hub

A production-minded starter for a Telegram SaaS bot that handles document conversion, image tools, OCR/AI workflows, referrals, credit limits, daily rewards, forced channel joins, analytics, and admin controls.

This repository is the first working foundation for the "complete version": bot + API + worker-ready service layer. The conversion functions are implemented as Python services and can be called from Telegram handlers, API endpoints, or background workers.

## MVP Features Included

- Telegram bot shell with menus for PDF tools, image tools, AI tools, resume center, referrals, credits, daily rewards, and admin commands
- FastAPI backend with health, stats, users, referrals, credits, and conversion job endpoints
- SQLite/PostgreSQL-compatible SQLAlchemy models
- Daily free limit and bonus-credit logic
- Referral code generation and reward accounting: each successful referral gives 3 bonus conversion tokens used after the free daily tier
- Admin command foundations: stats, broadcast, ban/unban, and user management
- File service modules for:
  - image to PDF
  - PDF to images
  - PDF merge/split/extract/rotate/password/unlock/compress
  - image format conversion/compression/resize/crop/watermark
  - zip/unzip bundles
  - OCR and AI placeholders with clean interfaces
- Docker Compose for Postgres + Redis
- Tests for quota/referral logic

## Quick Start

1. Create a bot with BotFather and copy the token.
2. Copy `.env.example` to `.env`.
3. Install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Start optional infrastructure:

```powershell
docker compose up -d
```

5. Run the API:

```powershell
uvicorn app.main:app --reload
```

6. Run the Telegram bot:

```powershell
python -m app.bot
```

## Environment

See `.env.example` for required and optional variables.

For local development, SQLite works out of the box. For production, use Postgres and Redis-backed workers.

Required for Telegram:

- `BOT_TOKEN`: from BotFather
- `ADMIN_IDS`: your numeric Telegram user ID, comma-separated for multiple admins
- `FORCED_CHANNEL`: optional channel username, for example `@YourChannel`

Optional AI APIs:

- `GROQ_API_KEY`: Groq-powered AI summarizer, quiz, resume, translation, and interview features
- `GROQ_MODEL`: default `llama-3.3-70b-versatile`
- `OPENAI_API_KEY`: optional fallback AI provider
- `REMOVE_BG_API_KEY`: background removal provider placeholder

## Deploy

### VPS / Docker

1. Copy `.env.example` to `.env` and fill your real tokens.
2. Use Postgres in production:

```env
DATABASE_URL=postgresql+psycopg://hub:hub@postgres:5432/hub
```

3. Start everything:

```powershell
docker compose up -d --build
```

4. Check API:

```powershell
curl http://YOUR_SERVER:8000/health
```

5. Open your Telegram bot and send `/start`.

### Railway / Render Style Hosts

Use these processes:

- API/web: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Bot worker: `python -m app.bot`

Add the same environment variables from `.env.example` in the hosting dashboard.

### Render

This repo includes `render.yaml` for a single free Render web service plus free Postgres. The Telegram bot runs through FastAPI webhooks at `/telegram/webhook`, so no separate background worker is required.

Required Render environment variables:

```env
BOT_TOKEN=your_botfather_token
ADMIN_IDS=@your_admin_username_or_numeric_id
FORCED_CHANNEL=@YourChannel
GROQ_API_KEY=your_groq_key
WEBHOOK_BASE_URL=https://your-render-service.onrender.com
```

After the first deploy, set `WEBHOOK_BASE_URL` to the real Render URL, then redeploy or restart the service so Telegram receives the webhook URL.

Free monitoring:

- Create a free UptimeRobot HTTP monitor for `https://your-render-service.onrender.com/health`
- Use the 5-minute interval
- See `monitoring/uptimerobot.md`

## API Endpoints

OpenAPI docs are available after launch at:

```text
http://YOUR_SERVER:8000/docs
```

Core:

- `GET /health`
- `GET /stats`
- `POST /users`
- `POST /jobs`
- `POST /ban`
- `POST /unban`
- `GET /tools/catalog`

PDF:

- `POST /tools/pdf/image-to-pdf`
- `POST /tools/pdf/to-images`
- `POST /tools/pdf/merge`
- `POST /tools/pdf/split`
- `POST /tools/pdf/compress`
- `POST /tools/pdf/protect`
- `POST /tools/pdf/unlock`
- `POST /tools/pdf/rotate`
- `POST /tools/pdf/extract`

Image:

- `POST /tools/image/convert`
- `POST /tools/image/compress`
- `POST /tools/image/resize`
- `POST /tools/image/crop`
- `POST /tools/image/watermark`

Archive:

- `POST /tools/archive/zip`
- `POST /tools/archive/unzip`

OCR:

- `POST /tools/ocr/image-to-text`
- `POST /tools/ocr/pdf-to-text`

AI:

- `POST /tools/ai/summarize`
- `POST /tools/ai/quiz`
- `POST /tools/ai/simplify`
- `POST /tools/ai/flashcards`
- `POST /tools/ai/interview`
- `POST /tools/ai/translate`

Resume:

- `POST /tools/resume/ats-score`
- `POST /tools/resume/improve`
- `POST /tools/resume/cover-letter`
- `POST /tools/resume/linkedin`

## What I Need To Deploy It Live

To connect this to your real Telegram bot, fill these values:

```env
BOT_TOKEN=
ADMIN_IDS=
FORCED_CHANNEL=
GROQ_API_KEY=
OPENAI_API_KEY=
```

Without `BOT_TOKEN`, the code is complete but cannot attach to Telegram.

## Architecture

```mermaid
flowchart LR
    U["Telegram User"] --> B["Telegram Bot"]
    B --> API["FastAPI Backend"]
    API --> DB["Postgres / SQLite"]
    API --> Q["Redis Queue"]
    Q --> W["Conversion Workers"]
    W --> S["File Storage"]
    W --> AI["AI / OCR Providers"]
    B --> S
    Admin["Admin"] --> API
```

## Next Production Steps

- Replace local filesystem storage with S3/R2.
- Add Redis Queue/RQ or Celery job execution for large conversions.
- Add payments later if you decide to sell plans.
- Add Telegram Mini App frontend.
- Add proper file cleanup lifecycle and virus scanning.
- Add deployed admin dashboard.
