import os
from aiohttp import web

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import load_config
from app.telegram.bot import build_bot, build_dispatcher
from app.storage.db import DB
from app.storage.repos.user_state_repo import UserStateRepo
from app.services.audit_service import AuditService

async def health(request: web.Request) -> web.Response:
    return web.Response(text="OK")

async def on_startup(app: web.Application) -> None:
    cfg = app["cfg"]
    bot = app["bot"]

    # Webhook URL = PUBLIC_BASE_URL + endpoint
    webhook_path = app["webhook_path"]
    webhook_url = f"{cfg.public_base_url}{webhook_path}"
    await bot.set_webhook(webhook_url)

async def on_shutdown(app: web.Application) -> None:
    await app["bot"].delete_webhook(drop_pending_updates=False)
    await app["db"].close()
    await app["bot"].session.close()

def create_app() -> web.Application:
    cfg = load_config()
    db = DB(cfg.database_url)

    bot = build_bot(cfg.bot_token)
    dp = build_dispatcher()

    app = web.Application()
    app["cfg"] = cfg
    app["db"] = db
    app["bot"] = bot

    app["webhook_path"] = "/telegram/webhook"

    # DI: прокидываем репозитории/сервисы в хендлеры aiogram
    user_state_repo = UserStateRepo(db)
    audit = AuditService(db)
    dp["user_state_repo"] = user_state_repo
    dp["audit"] = audit

    # health endpoint for UptimeRobot
    app.router.add_get("/health", health)

    # webhook endpoint
    request_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    request_handler.register(app, path=app["webhook_path"])
    setup_application(app, dp, bot=bot)

    async def connect_db(app: web.Application) -> None:
        app["db"].connect()

    app.on_startup.append(connect_db)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app

def main() -> None:
    app = create_app()
    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":

    main()

