from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.telegram.render import render_menu, render_help
from app.usecases.start import handle_start
from app.usecases.help import handle_help
from app.storage.repos.user_state_repo import UserStateRepo
from app.services.audit_service import AuditService

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, user_state_repo: UserStateRepo, audit: AuditService):
    user_id = message.from_user.id
    before = await user_state_repo.get_or_create(user_id)

    await handle_start(user_id, user_state_repo)

    after = await user_state_repo.get_or_create(user_id)
    text, kb = render_menu()
    await message.answer(text, reply_markup=kb)

    await audit.log(
        user_id=user_id,
        event_type="command",
        payload={"cmd": "/start"},
        mode_before=before.mode,
        screen_before=before.screen,
        mode_after=after.mode,
        screen_after=after.screen,
        result="ok",
    )

@router.message(Command("help"))
async def cmd_help(message: Message, user_state_repo: UserStateRepo, audit: AuditService):
    user_id = message.from_user.id
    before = await user_state_repo.get_or_create(user_id)

    await handle_help()

    after = await user_state_repo.get_or_create(user_id)
    text, kb = render_help()
    await message.answer(text, reply_markup=kb)

    await audit.log(
        user_id=user_id,
        event_type="command",
        payload={"cmd": "/help"},
        mode_before=before.mode,
        screen_before=before.screen,
        mode_after=after.mode,
        screen_after=after.screen,
        result="ok",
    )

@router.callback_query(F.data == "m:book")
async def cb_menu_book(call: CallbackQuery, audit: AuditService):
    # Заглушка: пока просто подтверждаем, что роутинг работает
    await call.answer()
    await call.message.answer("001", reply_markup=None)

    await audit.log(
        user_id=call.from_user.id,
        event_type="callback",
        payload={"data": call.data},
        mode_before=None,
        screen_before=None,
        mode_after=None,
        screen_after=None,
        result="ok",
    )

@router.callback_query(F.data == "m:q")
async def cb_menu_question(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Q1\nНапишите вопрос одним сообщением.")

@router.callback_query(F.data == "m:work")
async def cb_menu_work(call: CallbackQuery):
    await call.answer()
    # Место под ссылку (закомментировано, как ты просил):
    # link = "https://..."
    await call.message.answer("W1\n(Текст раздела «Как проходит работа» будет здесь.)")

@router.callback_query(F.data == "m:group")
async def cb_menu_group(call: CallbackQuery):
    await call.answer()
    await call.message.answer("G1\nВведите пароль для доступа к группе.")