from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Арендовать авто/мото')
client_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

client_keyboard.row(btn_1)