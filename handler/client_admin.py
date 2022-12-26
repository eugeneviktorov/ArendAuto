import sqlite3
from create_bot import cursor, conn, bot, kb_menus
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Filter, Command
from keyboards import admin_edit_keyboard, menus_keyboard, danet_kb, create_keyboard


# FSM машина состояний авторизации
class login(StatesGroup):
    login_start = State()
    login_step_1 = State()
    edit_menu = State()
    edit_menu_step_2 = State()
    add_photo = State()
    add_name = State()
    add_description = State()
    add_price = State()
    add_term = State()
    add_product = State()
    delete_product = State()


# Обработчик команды login
async def command_login(message: types.Message):
    await message.answer("Войдите в систему администрирования!\n\nВведите логин:")
    await login.login_start.set()


# Авторизация: шаг 1
async def login_step_1(message: types.Message, state: FSMContext):
    # Сохраняем введенный логин в state
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await login.next()


# Авторизация: шаг 2
async def login_step_2(message: types.Message, state: FSMContext):
    # Сохраняем введенный пароль в state
    await state.update_data(password=message.text)
    data = await state.get_data()
    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()
    if data["login"] in admin[2] and data["password"] == admin[2]:
        await message.answer("Вы вошли в систему!\nВ какой пункт хотите внести изменения?", reply_markup=menus_keyboard)
        await login.next()
    else:
        await message.answer("Неверный логин или пароль\n\nПопробуйте ещё раз: /login")
        await state.finish()


async def edit_menu(message: types.Message, state: FSMContext):
    if message.text in kb_menus.keys():
        cursor.execute(f"SELECT Name FROM {kb_menus[message.text]}")
        result = cursor.fetchall()
        await state.update_data(CurrentMenu=kb_menus[message.text])
        await state.update_data(CurrentMenuE=create_keyboard(result), CurrentMenu=kb_menus[message.text])

        await message.answer("Добавить или удалить авто/мото?", reply_markup=admin_edit_keyboard)
        await login.next()


async def edit_menu_step_2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "Добавить":
        await state.update_data(Action="add")
        await message.answer("Вставьте фотографию:")
        await login.next()
    elif message.text == "Удалить":
        await message.answer("Выбирете авто/мото для удаления", reply_markup=data["CurrentMenuE"])
        await login.delete_product.set()


async def add_photo(message: types.Message, state: FSMContext):
    file_info = await bot.get_file(message.photo[-1].file_id)
    path = "./images/ADDED/" + file_info.file_path.split('photos/')[1]
    await message.photo[-1].download(destination_file=path)
    await state.update_data(ImagePath=path)
    await bot.send_message(message.from_user.id, "Введите название авто/мото:")
    await login.next()


async def add_name(message: types.Message, state: FSMContext):
    NameLength = 1
    if len(message.text) >= NameLength:
        await state.update_data(Name=message.text)
        await message.answer("Введите описание авто/мото:")
        await login.next()
    else:
        await message.answer("Название слишком короткое, попробуйте еще раз")


async def add_description(message: types.Message, state: FSMContext):
    DescriptionLength = 5
    if len(message.text) >= DescriptionLength:
        await state.update_data(Description=message.text)
        await message.answer("Введите цену товара:")
        await login.next()
    else:
        await message.answer("Описание слишком короткое, попробуйте еще раз")


async def add_price(message: types.Message, state: FSMContext):
    MinimalPrice = 9999
    try:
        if int(message.text) > MinimalPrice:
            await state.update_data(Price=int(message.text))
            await message.answer("Введите минимальное количество дней для аренды:")
            await login.next()
        else:
            await message.answer("Вы ввели маленькую сумму, попробуйте еще раз!\nМинимальная сумма 10000₽")
    except ValueError:
        await message.answer("Ошибка!!!\nВведите цену в корректном формате без лишних символов\nНапример: 250")


async def add_term(message: types.Message, state: FSMContext):
    MinimalTerm = 0
    try:
        if int(message.text) > MinimalTerm:
            data = await state.get_data()
            await state.update_data(Term=int(message.text))

            with open(data["ImagePath"], "rb") as bc:
                await message.answer_photo(bc.read(), caption=data["Name"]
                    + "\n\nОписание: " + str(data["Description"])
                    + "\n\nЦена:" + str(data["Price"]) + "₽"
                    + "\nДней: " + message.text)

            await bot.send_message(message.from_user.id, "Хотите добавить авто/мото?", reply_markup=danet_kb)
            await login.next()
        else:
            await message.answer("Вы ввели маленький срок аренды, попробуйте еще раз!\nМинимальная срок 1 день")
    except ValueError:
            await message.answer("Ошибка!!!\nВведите кол-во дней в корректном формате без лишних символов\nНапример: 1")


async def add_product(message: types.Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        cursor.execute(
            f"INSERT INTO {data['CurrentMenu']} (Name, Price, Photo, Description, Term) VALUES (?,?,?,?,?)", (data["Name"], data["Price"], data["ImagePath"], data["Description"], data["Term"]))
        await message.answer("Авто/мото успешно добавлено! \nПродолжить администрирование: /login \nАрендовать авто/мото: /start")
        await state.finish()


async def delete_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute(f'SELECT Name FROM {data["CurrentMenu"]}')
    result = cursor.fetchall()
    products=[]
    for i in result: products.append(i[0])
    if message.text in products :
        cursor.execute(F'DELETE FROM {data["CurrentMenu"]} WHERE Name=?',(message.text,))
        conn.commit()
        await message.answer(f'Вы удалили модель авто/мото: {message.text} \nПродолжить администрирование: /login \nАрендовать авто/мото: /start')
        await state.finish()


def admin_handlers_register(dp: Dispatcher):
    dp.register_message_handler(command_login, Command(['login']))

    dp.register_message_handler(login_step_1, state=login.login_start)
    dp.register_message_handler(login_step_2, state=login.login_step_1)
    dp.register_message_handler(edit_menu, state=login.edit_menu)
    dp.register_message_handler(edit_menu_step_2, state=login.edit_menu_step_2)

    dp.register_message_handler(add_photo, state=login.add_photo, content_types=['photo'])
    dp.register_message_handler(add_name, state=login.add_name)
    dp.register_message_handler(add_description, state=login.add_description)
    dp.register_message_handler(add_price, state=login.add_price)
    dp.register_message_handler(add_term, state=login.add_term)
    dp.register_message_handler(add_product, state=login.add_product)
    dp.register_message_handler(delete_product, state=login.delete_product)