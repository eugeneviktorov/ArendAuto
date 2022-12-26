from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

def create_keyboard(arr):
    menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in arr:
        menu_kb.insert(KeyboardButton(i[0]))
    return menu_kb.add(KeyboardButton('Назад')).add(KeyboardButton('Подтвердить'))

btn_1 = KeyboardButton('Продолжить')
btn_2 = KeyboardButton('Подтвердить')
btn_3 = KeyboardButton('Выйти')

order_keyboard_1 = ReplyKeyboardMarkup(resize_keyboard=True)
order_keyboard_1.row(btn_1, btn_2, btn_3)