import os
from aiohttp import web
from aiogram.types import Update

from app.config import load_config
from app.telegram.bot import build_bot, build_dispatcher
from app.storage.db import DB
from app.storage.repos.user_state_repo import UserStateRepo
from app.services.audit_service import AuditService

WEBHOOK_PATH = "/telegram/webhook"


async def telegram_webhook(request: web.Request) -> web.Response:
    bot = request.app["bot"]
    dp = request.app["dp"]

    data = await request.json()
    update = Update.model_validate(data)  # aiogram v3 / pydantic v2
    await dp.feed_update(bot, update)

    return web.Response(text="OK")


async def health(request: web.Request) -> web.Response:
    return web.Response(text="OK")


async def on_startup(app: web.Application) -> None:
    cfg = app["cfg"]
    bot = app["bot"]

    webhook_path = app["webhook_path"]
    webhook_url = f"{cfg.public_base_url}{webhook_path}"
    await bot.set_webhook(webhook_url)


async def on_shutdown(app: web.Application) -> None:
    # db close не нужен: мы открываем соединения "по месту" через with psycopg.connect(...)
    await app["bot"].delete_webhook(drop_pending_updates=False)
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
    app["dp"] = dp

    app["webhook_path"] = WEBHOOK_PATH

    # DI: прокидываем репозитории/сервисы в хендлеры aiogram
    user_state_repo = UserStateRepo(db)
    audit = AuditService(db)
    dp["user_state_repo"] = user_state_repo
    dp["audit"] = audit

    # health endpoint for UptimeRobot
    app.router.add_get("/health", health)

    app.router.add_get(app["webhook_path"], lambda r: web.Response(text="WEBHOOK OK"))
    app.router.add_post(app["webhook_path"], telegram_webhook)

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

