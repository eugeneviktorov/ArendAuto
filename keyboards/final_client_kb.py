from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Подтвердить')
btn_2 = KeyboardButton('Вернуться назад')

final_client_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
final_client_kb.row(btn_1, btn_2)