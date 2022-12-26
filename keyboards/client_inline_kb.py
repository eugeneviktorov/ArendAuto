from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

info_inline_btn_1 = InlineKeyboardButton('Выбрать', callback_data='add')
info_inline_btn_2 = InlineKeyboardButton('Отменить', callback_data='notAdd')

inline_client_keyboard = InlineKeyboardMarkup().add(info_inline_btn_1).add(info_inline_btn_2)