from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import ContentType

from config import admin_id
from load_all import dp, bot
from states import NewItem, Mailing
from database import Accessories, User, Malling, Other, Pants, Shoes, Hats


@dp.message_handler(user_id=admin_id, commands=["admin_panel"])
async def admin_panel(message: types.Message):
    admin_panel_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Добавить товар", callback_data="add_item")],
            [
                InlineKeyboardButton(text="Сделать рассылку", callback_data="mailing"),
                InlineKeyboardButton(text="Удалить товар", callback_data="dell_item"),
                InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")
            ]
        ]
    )
    await message.answer("Что вы хотите сделать?", reply_markup=admin_panel_markup)

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


@dp.message_handler(user_id=admin_id, text_contains="add_accessories")
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()

@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_hat_name(message: types.Message, state: FSMContext):
    accessories_name = message.text
    accessories = Accessories()
    accessories.accessories_name = accessories_name

    await message.answer(("Название: {accessories_name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(accessories_name=accessories_name))

    await NewItem.Photo.set()
    await state.update_data(accessories=accessories)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    accessories_photo = message.photo[-1].file_id
    data = await state.get_data()
    accessories: Accessories = data.get("accessories")
    accessories.accessories_photo = accessories_photo

    await message.answer_photo(
        accessories_photo=accessories_photo,
        caption=("Название: {accessories_name}"
                  '\nПришлите мне цену товара или нажмите "Отмена"').format(name=accessories.accesories_name))

    await NewItem.Price.set()
    await state.update_data(accessories=accessories)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accessories: Accessories = data.get("accessories")
    try:
        accessories_price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    accessories.accessories_price = accessories_price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {accessories_price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(accessories_price=accessories_price),
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


@dp.message_handler(user_id=admin_id, text_contains="add_hat")
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    hat_name = message.text
    hats = Hats()
    hats.hat_name = hat_name

    await message.answer(("Название: {hat_name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(hat_name=hat_name))

    await NewItem.Photo.set()
    await state.update_data(hats=hats)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    hat_photo = message.photo[-1].file_id
    data = await state.get_data()
    hats: Hats = data.get("hats")
    Hats.hat_photo = hat_photo

    await message.answer_photo(
        hat_photo=hat_photo,
        caption=("Название: {hat_name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(name=hats.hat_name))

    await NewItem.Price.set()
    await state.update_data(hats=hats)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    hats: Hats = data.get("hats")
    try:
        hat_price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    hats.hat_price = hat_price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {hat_price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(hat_price=hat_price),
                         reply_markup=markup)
    await state.update_data(hats=hats)
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
    hats: Hats = data.get("hats")
    await hats.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, text_contains="add_malling")
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    malling_name = message.text
    malling = Malling()
    malling.malling_name = malling_name

    await message.answer(("Название: {malling_name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(malling_name=malling.malling_name))

    await NewItem.Photo.set()
    await state.update_data(malling=malling)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    malling_photo = message.photo[-1].file_id
    data = await state.get_data()
    malling: Malling = data.get("malling")
    malling.malling_photo = malling_photo

    await message.answer_photo(
        malling_photo=malling_photo,
        caption=("Название: {malling_name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(malling=malling.malling_name))

    await NewItem.Price.set()
    await state.update_data(malling=malling)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    malling: Malling = data.get("malling")
    try:
        malling_price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    malling.malling_price = malling_price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {malling_price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(malling_price=malling_price),
                         reply_markup=markup)
    await state.update_data(malling=malling)
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
    malling: Malling = data.get("malling")
    await malling.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, text_contains="add_pants")
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    pants_name = message.text
    pants = Pants()
    pants.pants_name = pants_name

    await message.answer(("Название: {pants_name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(pants_name=pants_name))

    await NewItem.Photo.set()
    await state.update_data(pants=pants)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    pants_photo = message.photo[-1].file_id
    data = await state.get_data()
    pants: Pants = data.get("pants")
    pants.pants_photo = pants_photo

    await message.answer_photo(
        pants_photo=pants_photo,
        caption=("Название: {pants_name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(pants_name=pants.pants_name))

    await NewItem.Price.set()
    await state.update_data(pants=pants)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pants: Pants = data.get("pants")
    try:
        pants_price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    pants.pants_price = pants_price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {pants_price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(pants_price=pants_price),
                         reply_markup=markup)
    await state.update_data(pants=pants)
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
    pants: Pants = data.get("pants")
    await pants.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, text_contains="add_shoes")
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()

@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    shoes_name = message.text
    shoes = Shoes()
    shoes.shoes_name = shoes_name

    await message.answer(("Название: {shoes_name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(shoes_name=shoes_name))

    await NewItem.Photo.set()
    await state.update_data(shoes=shoes)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    shoes_photo = message.photo[-1].file_id
    data = await state.get_data()
    shoes: Shoes = data.get("shoes")
    shoes.shoes_photo = shoes_photo

    await message.answer_photo(
        shoes_photo=shoes_photo,
        caption=("Название: {shoes_name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(shoes_name=shoes.shoes_name))

    await NewItem.Price.set()
    await state.update_data(shoes=shoes)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    shoes: Shoes = data.get("shoes")
    try:
        shoes_price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    shoes.shoes_price = shoes_price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {shoes_price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(shoes_price=shoes_price),
                         reply_markup=markup)
    await state.update_data(shoes=shoes)
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
    shoes: Shoes = data.get("shoes")
    await shoes.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, text_contains="add_other")
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    other_name = message.text
    other = Other()
    other.other_name = other_name

    await message.answer(("Название: {other_name}"
                           "\nПришлите мне фотографию товара (не документ) или нажмите /cancel").format(other_name=other_name))

    await NewItem.Photo.set()
    await state.update_data(other=other)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    other_photo = message.photo[-1].file_id
    data = await state.get_data()
    other: Other = data.get("other")
    other.other_photo = other_photo

    await message.answer_photo(
        other_photo=other_photo,
        caption=("Название: {other_name}"
                  "\nПришлите мне цену товара в копейках или нажмите /cancel").format(other_name=other.other_name))

    await NewItem.Price.set()
    await state.update_data(other=other)


@dp.message_handler(user_id=admin_id, state=NewItem.Price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    other: Other = data.get("other")
    try:
        other_price = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return

    other.other_price = other_price
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm")],
            [InlineKeyboardButton(text=("Ввести заново"), callback_data="change")],
        ]
    )
    await message.answer(("Цена: {other_price:,}\n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(other_price=other_price),
                         reply_markup=markup)
    await state.update_data(other=other)
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
    other: Other = data.get("other")
    await other.create()
    await call.message.answer("Товар удачно создан.")
    await state.reset_state()



# Фича для рассылки по юзерам (учитывая их язык)
@dp.callback_query_handler(user_id=admin_id, text_contains=["mailing"])
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
