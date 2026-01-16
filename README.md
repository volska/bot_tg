## bot_tg (Render + Neon + Webhook)

### Env
Copy .env.example to .env and fill values.

### Local run
pip install -r requirements.txt
export $(cat .env | xargs)
python -m app.main

### Migrations
Run SQL in order:
- migrations/001_schema.sql
- migrations/002_seed_slots.sql
(через psql или любой клиент к Neon)

### Render
Deploy as Web Service.
Set env vars in Render dashboard:
BOT_TOKEN, PUBLIC_BASE_URL, DATABASE_URL, etc.

### UptimeRobot
Ping:
https://<your-render-domain>/health
every 5 minutes.