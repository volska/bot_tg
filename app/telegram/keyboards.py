from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb() -> InlineKeyboardMarkup:
    # Как у Chat Norris: inline кнопки под сообщением
    buttons = [
        [InlineKeyboardButton(text="Записаться на сессию", callback_data="m:book")],
        [InlineKeyboardButton(text="Задать вопрос", callback_data="m:q")],
        [InlineKeyboardButton(text="Как проходит работа", callback_data="m:work")],
        [InlineKeyboardButton(text="Терапевтическая группа", callback_data="m:group")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)