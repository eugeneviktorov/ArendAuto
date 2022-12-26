from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Вернуться назад')

back_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
back_kb.row(btn_1)