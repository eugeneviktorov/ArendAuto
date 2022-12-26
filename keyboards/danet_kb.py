from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Да')
btn_2 = KeyboardButton('Нет')
btn_3 = KeyboardButton('Вернуться назад')

danet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
danet_kb.row(btn_1, btn_2, btn_3)