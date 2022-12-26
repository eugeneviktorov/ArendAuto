from create_bot import cursor, conn, bot, kb_menus
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from keyboards import client_keyboard, danet_kb, back_kb, final_client_kb, menus_keyboard, admin_edit_kb, create_keyboard, inline_client_keyboard
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from keyboards.edit_inline_kb import create_inline_kb


async def command_start(message: types.Message):
    await message.answer("Добро пожаловать в ArendAuto!", reply_markup=client_keyboard)

class menu(StatesGroup):
    input_order_is_start = State()
    order_step_1 = State()
    order_step_2 = State()
    order_edit = State()
    order_edit_2 = State()
    order_final_step = State()


async def order_start(message: types.Message, state: FSMContext):
    if message.text == "Арендовать авто/мото":
        await message.answer("Выберите транспорт:", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()
        await state.update_data(order_list={"mercedes":[], "bmw":[], "porsche":[], "motorcycles":[], "ferrari": [], "rolls": []})

async def order_step_1(message: types.Message, state: FSMContext):

    # Проверка является ли сообщение одним из списка
    if message.text in kb_menus.keys():
        await state.update_data(menu_type=kb_menus[message.text])

        # Делаем запрос в БД
        cursor.execute(f"SELECT Name FROM {kb_menus[message.text]}")
        result = cursor.fetchall()

        # Заполняем массив с авто/мото из текущего списка
        foodArr = []
        for i in result:
            foodArr.append(i[0])

        # Сохраняем массив с авто/мото из текущего меню в памяти
        await state.update_data(foodArr=foodArr)

        # Сохраняем текущую клавиатуру
        await state.update_data(cur_menu_kb=create_keyboard(result))
        data = await state.get_data()
        cur_menu_local = data["cur_menu_kb"]
        await message.answer(f"Выбрано: {message.text} \nВыберете Модель:", reply_markup=cur_menu_local)
        await menu.next()

    elif message.text == "Выход":
        await message.answer("Вы вышли в главное меню.", reply_markup=client_keyboard)
        await state.finish()

async def order_step_2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == 'Назад':
        await message.answer(f"Выберите другой транспорт", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()

    elif message.text == "Подтвердить":
        await message.answer("Хотите изменить список аренды?", reply_markup=danet_kb)
        await menu.order_edit.set()

    elif message.text in data["foodArr"]:
        cursor.execute(f"SELECT * FROM {data['menu_type']} WHERE Name = ?", (message.text,))
        product = cursor.fetchone()
        await state.update_data(cur_product=[data['menu_type'], product[0]])
        with open(product[3], "rb") as bc:
            await message.answer_photo(bc.read(), "Модель: " + str(product[1]) + "\n\n" + str(product[4]) + "\n\nЦена: " + str(product[2]) + "₽ / " + str(product[5] + " день"), reply_markup=inline_client_keyboard)
        await menu.next()


async def order_step_3(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback_query.data == "add":

        # Добавление в список
        old_order_list = data["order_list"]
        cur_menu = data["cur_product"][0]
        cur_product_id = data["cur_product"][1]
        old_order_list[cur_menu].append(cur_product_id)
        await state.update_data(order_list=old_order_list)

        order_message = "Ваш список:\n"
        final_price = 0
        for key in data["order_list"].keys():
            if data["order_list"][key] != []:
                for el in data["order_list"][key]:
                    cursor.execute(f"SELECT Name,Price FROM {key} WHERE id = {el}")
                    product = cursor.fetchone()
                    final_price += product[1]
                    order_message += product[0] + " - " + str(product[1]) + "₽\n"
        order_message += "Итоговая цена за аренду: " + str(final_price) + "₽"

        await bot.send_message(callback_query.from_user.id, f'Вы добавили авто/мото в список аренды!\n\n{order_message}', reply_markup=data["cur_menu_kb"])
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await menu.order_step_1.set()
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы отменили выбор! \nВы можете выбрать другую модель.', reply_markup=data["cur_menu_kb"])
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await menu.order_step_1.set()


# Функция обработчик выбора --- редактировать ли список аренды?
async def order_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "Да":
        accept = False
        for item in data["order_list"]:
            if item:
                accept = True
        if accept:
            ine_bt = create_inline_kb(data["order_list"])
            await message.answer("Выберите то-что вы хотите убрать из списка:", reply_markup=ine_bt)
            await menu.next()
        else:
            await message.answer("Вы ничего не выбрали, вернитесь назад.", reply_markup=back_kb)


    elif message.text == "Нет":
        # Формирование сообщения с корзиной
        order_message = "Ваша корзина:\n"
        final_price = 0
        for key in data["order_list"].keys():
            if data["order_list"][key] != []:
                for el in data["order_list"][key]:
                    cursor.execute(f"SELECT Name,Price FROM {key} WHERE id = {el}")
                    product = cursor.fetchone()
                    final_price += product[1]
                    order_message += product[0] + " - " + str(product[1]) + "₽\n"
        order_message += "Итого: " + str(final_price) + "₽"

        await message.answer(order_message + "\n\n" + "Для подтверждения нажмите подтвердить!", reply_markup=final_client_kb)
        await menu.order_final_step.set()

    elif message.text == "Вернуться назад":
        await message.answer("Выберете Марку:", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()

# Обработчик редактирования аренды
async def order_edit_2(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    arr = callback_query.data.split(":")
    new_list = data["order_list"][arr[0]]
    new_list.remove(int(arr[1]))
    new_order_list = data["order_list"]
    new_order_list[arr[0]] = new_list
    await state.update_data(order_list=new_order_list)
    await bot.send_message(
            callback_query.from_user.id,
            'Вы убрали авто/мото из списка аренды, хотите еще что-нибудь изменить?', reply_markup=danet_kb)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await menu.order_edit.set()

async def order_final_step(message: types.Message, state: FSMContext):
    if message.text == "Подтвердить":
        data = await state.get_data()
        user_id = message.from_user.id
        def getStrOrder(arr):
            strOrder=""
            for i in arr:
                strOrder+= str(i) + ","
            if strOrder != "":
                return strOrder[:-1]
            else:
                return "-1"
        motorcycles = getStrOrder(data["order_list"]["motorcycles"])
        mercedes = getStrOrder(data["order_list"]["mercedes"])
        ferrari = getStrOrder(data["order_list"]["ferrari"])
        porsche = getStrOrder(data["order_list"]["porsche"])
        rolls = getStrOrder(data["order_list"]["rolls"])
        bmw = getStrOrder(data["order_list"]["bmw"])

        cursor.execute(f"INSERT INTO orders (user_id, mercedes, bmw, porsche, motorcycles, ferrari, rolls) VALUES (?,?,?,?,?,?,?)",(user_id, mercedes, bmw, porsche, motorcycles, ferrari, rolls))
        conn.commit()

        await message.answer("Благодарим вас. Ваш выбор принят! \n\nС вами свяжется наш сотрудник для подтверждения информации. \n\nАдрес где можно забрать авто/мото: Ленина 1а", reply_markup=client_keyboard)
        await state.finish()
    elif message.text == "Вернуться назад":
        await message.answer("Хотите что-нибудь изменить?", reply_markup=danet_kb)
        await menu.order_edit.set()

async def command_help(message: types.Message):
    await message.reply("Техническая поддержка: @eugeneviktorov")

async def command_login(message: types.Message):
    await message.reply()


# Регистрация функций
def client_handlers_register(dp : Dispatcher):
    dp.register_message_handler(command_start, Command(['start']))
    dp.register_message_handler(command_help, Command(['help']))
    dp.register_message_handler(command_login, Command(['login']))

    dp.register_message_handler(order_start)
    dp.register_message_handler(order_step_1, state=menu.input_order_is_start)
    dp.register_message_handler(order_step_2, state=menu.order_step_1)
    dp.register_message_handler(order_edit, state=menu.order_edit)
    dp.register_message_handler(order_final_step, state=menu.order_final_step)
    dp.register_callback_query_handler(order_step_3, state=menu.order_step_2, text=['add', 'notAdd'])
    dp.register_callback_query_handler(order_edit_2, state=menu.order_edit_2)