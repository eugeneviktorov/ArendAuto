from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import cursor


def create_inline_kb(cb_data):
    inline_client_keyboard = InlineKeyboardMarkup()
    for key in cb_data.keys():
        for id in cb_data[key]:
            cursor.execute(f"SELECT Name FROM {key} WHERE id = {id}")
            res = cursor.fetchone()
            inline_client_keyboard.add(InlineKeyboardButton(res[0], callback_data=str(key)+":"+str(id)))
    return inline_client_keyboard