from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.callback_query import CallbackQuery

from config import admin_id
from load_all import dp, bot
from states import NewItem, Mailing
from database import Accessories, Item, User, Malling, Other, Pants, Shoes


@dp.message_handler(user_id=admin_id, commands=["cancel"], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили создание товара")
    await state.reset_state()

@dp.callback_query_handler(user_id=admin_id, text_contains="admin_panel")
async def admin_panel(call: CallbackQuery):
    admin_panel_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Добавить товар", callback_data="add_item")],
            [
                InlineKeyboardButton(text="Сделать рассылку", callback_data="malling"),
                InlineKeyboardButton(text="Удалить товар", callback_data="dell_item"),
                InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")
            ]
        ]
    )
    await call.message.answer("Что вы хотите сделать?", reply_markup=admin_panel_markup)

@dp.callback_query_handler(user_id=admin_id, text_contains="add_item")
async def item_category(call: CallbackQuery):
    categories_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Головные уборы", callback_data="add_hat")],
            [
                InlineKeyboardButton(text="Аксессуары", callback_data="add_accessories"),
                InlineKeyboardButton(text="Верхняя одежда", callback_data="add_malling"),
                InlineKeyboardButton(text="Брюки", callback_data="add_pants"),
                InlineKeyboardButton(text="Обувь", callback_data="addshoes"),
                InlineKeyboardButton(text="Другое", calback_data="add_other"),
                InlineKeyboardButton(text="Отмена", callback_data="add_cancel")
            ]
        ]
    )

    await call.message.answer("Выберите в какую категорию вы хотите добавить товар:", reply_markup=categories_markup)

#########################
@dp.message_handler(user_id=admin_id, state=NewItem.Categories)
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()

@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_hat_name(message: types.Message, state: FSMContext):
    name = message.text
    accessories = Accessories()
    accessories.accessories_name = name

    await message.answer(("Название: {name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(name=name))

    await NewItem.Photo.set()
    await state.update_data(accessories=accessories)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    accessories: Accessories = data.get("acessories")
    accessories.accessories_photo = photo

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  '\nПришлите мне цену товара или нажмите "Отмена"').format(name=accessories.accesories_name))

    await NewItem.Price.set()
    await state.update_data(accessories=accessories)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accessories: Accessories = data.get("accessories")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    accessories.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(accessories=accessories)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите цену товара заново")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    accessories: Accessories = data.get("accessories")
    await accessories.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()

################################################
@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(("Название: {name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товара в копейках")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()

################################################
@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(("Название: {name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товара в копейках")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()

################################################

@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(("Название: {name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товара в копейках")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()

################################################
@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(("Название: {name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товара в копейках")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()

################################################
@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name

    await message.answer(("Название: {name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(name=name))

    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(name=item.name))

    await NewItem.Price.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price / 100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товара в копейках")
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()

################################################



# Фича для рассылки по юзерам (учитывая их язык)
@dp.callback_query_handler(user_id=admin_id, text_contains=["malling"])
async def mailing(call: CallbackQuery):
    await call.message.answer("Пришлите текст рассылки")
    await Mailing.Mall.set()

@dp.callback_query_handler(user_id=admin_id, state=Mailing.Mall)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    await state.reset_state()
    await call.message.edit_reply_markup()

    users = await User.query.where().gino.all()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id,
                                   text=text)
            await sleep(0.3)
        except Exception:
            pass
    await call.message.answer("Рассылка выполнена.")
