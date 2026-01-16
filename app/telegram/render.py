from aiogram.types import InlineKeyboardMarkup
from app.telegram.keyboards import main_menu_kb

def render_menu() -> tuple[str, InlineKeyboardMarkup]:
    return ("Главное меню", main_menu_kb())

def render_help() -> tuple[str, InlineKeyboardMarkup]:
    text = (
        "Справка\n\n"
        "/start — открыть главное меню\n"
        "/help — открыть эту справку\n\n"
        "Для записи на сессию используйте кнопки в меню."
    )
    return (text, main_menu_kb())