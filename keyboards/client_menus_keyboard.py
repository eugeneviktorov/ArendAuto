from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('BMW')
btn_2 = KeyboardButton('Mercedes')
btn_3 = KeyboardButton('Porsche')
btn_4 = KeyboardButton('Ferrari')
btn_5 = KeyboardButton('Rolls-Royce')
btn_6 = KeyboardButton('Мотоциклы')

menus_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

menus_keyboard.row(btn_1, btn_2, btn_3)
menus_keyboard.row(btn_4, btn_5, btn_6).row(KeyboardButton('Выход'))