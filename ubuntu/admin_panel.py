from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, reply_keyboard
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import ContentType
from sqlalchemy.sql.expression import text

from config import admin_id
from load_all import dp, bot
from states import(NewHats, Mailing, NewAccessories, NewMalling, NewOther, NewPants, NewShoes)
from database import Accessories, User, Malling, Other, Pants, Shoes, Hats


@dp.callback_query_handler(text_contains="cancel", state='*')
async def cancel(call: CallbackQuery, state: FSMContext):
    await state.finish()
    chat_id = call.from_user.id

    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Список товаров", callback_data="list_categories")],
            [
                InlineKeyboardButton(text="Наш магазин", callback_data='storage'),
                InlineKeyboardButton(text="Поддержка", callback_data="help")
            ]
        ]
    )

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"

    text = ("Действие отменено.\n")
    if call.from_user.id == admin_id:
        text += ("Чтобы увидеть админ-панель нажмите:\n /admin_panel")
    await bot.send_message(chat_id, text, reply_markup=markup)


@dp.message_handler(user_id=admin_id, commands=["admin_panel"])
async def admin_panel(message: types.Message):
    admin_panel_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Сделать рассылку", callback_data="mailing")],
            [
                InlineKeyboardButton(text="Добавить товар", callback_data="add_item"),
                InlineKeyboardButton(text="Удалить товар", callback_data="dell_item"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    await message.answer("Что вы хотите сделать?", reply_markup=admin_panel_markup)

@dp.callback_query_handler(user_id=admin_id, text_contains="add_item")
async def item_category(call: CallbackQuery):
    chat_id = call.from_user.id
    categories_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Головные уборы", callback_data="add_hat")],
            [
                InlineKeyboardButton(text="Аксессуары", callback_data="add_accessories"),
                InlineKeyboardButton(text="Верхняя одежда", callback_data="add_malling")],
            [
                InlineKeyboardButton(text="Брюки", callback_data="add_pants"),
                InlineKeyboardButton(text="Обувь", callback_data="add_shoes")],
            [
                InlineKeyboardButton(text="Другое", callback_data="add_other"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    text = (
            "Выберите в какую категорию вы хотите добавить товар:")
    await bot.send_message(chat_id, text, reply_markup=categories_markup)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_accessories")
async def add_accessories(call: CallbackQuery):
    chat_id = call.from_user.id
    text = ("Введите название товара или нажмите:")
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await bot.send_message(chat_id, text, reply_markup=button)
    await NewAccessories.Name.set()

@dp.message_handler(user_id=admin_id, state=NewAccessories.Name)
async def enter_accessories_name(message: types.Message, state: FSMContext):
    accessories_name = message.text
    accessories = Accessories()
    accessories.accessories_name = accessories_name
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )


    await message.answer("Название: {accessories_name}"
                           '\nПришлите мне фотографию товара (не документ) или нажмите "Отмена"'.format(accessories_name=accessories_name), 
                           reply_markup=button)

    await NewAccessories.Photo.set()
    await state.update_data(accessories=accessories)


@dp.message_handler(user_id=admin_id, state=NewAccessories.Photo, content_types=ContentType.PHOTO)
async def add_accessories_photo(message: types.Message, state: FSMContext):
    accessories_photo = message.photo[-1].file_id
    data = await state.get_data()
    accessories: Accessories = data.get("accessories")
    accessories.accessories_photo = accessories_photo
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    chat_id = message.from_user.id
    text = ("Название: {accessories_name}"
                  '\nПришлите мне цену товара или нажмите "Отмена"')

    await bot.send_photo(chat_id, accessories_photo,
        caption=text.format(accessories_name=accessories.accessories_name),
        reply_markup=button)

    await NewAccessories.Price.set()
    await state.update_data(accessories=accessories)


@dp.message_handler(user_id=admin_id, state=NewAccessories.Price)
async def enter_accessories_price(message: types.Message, state: FSMContext):
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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await message.answer("Цена: {accessories_price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить'.format(accessories_price=accessories_price),
                        reply_markup=markup)
    await state.update_data(accessories=accessories)
    await NewAccessories.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewAccessories.Confirm)
async def enter_accessories_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите цену товара заново")
    await NewAccessories.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewAccessories.Confirm)
async def enter_accessories_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    accessories: Accessories = data.get("accessories")
    await accessories.create()
    await call.message.answer("Товар успешно создан.")
    await state.reset_state()


@dp.callback_query_handler(user_id=admin_id, text_contains="add_hat")
async def add_hat(call: CallbackQuery):
    chat_id = call.from_user.id
    text = ("Введите название товара или нажмите:")
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await bot.send_message(chat_id, text, reply_markup=button)
    await NewHats.Name.set()


@dp.message_handler(user_id=admin_id, state=NewHats.Name)
async def enter_hat_name(message: types.Message, state: FSMContext):
    hat_name = message.text
    hats = Hats()
    hats.hat_name = hat_name
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await message.answer("Название: {hat_name}"
                           '\nПришлите фотографию товара (не документ) или нажмите "Отмена"'.format(hat_name=hat_name),
                           reply_markup=button)

    await NewHats.Photo.set()
    await state.update_data(hats=hats)


@dp.message_handler(user_id=admin_id, state=NewHats.Photo, content_types=ContentType.PHOTO)
async def add_hat_photo(message: types.Message, state: FSMContext):
    hat_photo = message.photo[-1].file_id
    text = ("Название: {hat_name}" 
            '\nПришлите мне цену товара или нажмите "Отмена"')
    data = await state.get_data()
    hats: Hats = data.get("hats")
    hats.hat_photo = hat_photo
    button = InlineKeyboardMarkup(
    button = InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    chat_id = message.from_user.id

    await bot.send_photo(chat_id,
        hat_photo,
        caption=text.format(hat_name=hats.hat_name),
        reply_markup=button)

    await NewHats.Price.set()
    await state.update_data(hats=hats)


@dp.message_handler(user_id=admin_id, state=NewHats.Price)
async def enter_hat_price(message: types.Message, state: FSMContext):
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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await message.answer("Цена: {hat_price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить'.format(hat_price=hat_price),
                         reply_markup=markup)
    await state.update_data(hats=hats)
    await NewHats.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewHats.Confirm)
async def enter_hat_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите цену товара заново")
    await NewHats.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewHats.Confirm)
async def enter_hat_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    hats: Hats = data.get("hats")
    await hats.create()
    await call.message.answer("Товар успешно создан.")
    await state.reset_state()


@dp.callback_query_handler(user_id=admin_id, text_contains="add_malling")
async def add_malling(call: CallbackQuery):
    chat_id = call.from_user.id
    text = ("Введите название товара или нажмите:")
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await bot.send_message(chat_id, text, reply_markup=button)
    await NewMalling.Name.set()


@dp.message_handler(user_id=admin_id, state=NewMalling.Name)
async def enter_malling_name(message: types.Message, state: FSMContext):
    malling_name = message.text
    malling = Malling()
    malling.malling_name = malling_name
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await message.answer("Название: {malling_name}"
                           '\nПришлите фотографию товара (не документ) или нажмите "Отмена"'.format(malling_name=malling.malling_name),
                           reply_markup=button)

    await NewMalling.Photo.set()
    await state.update_data(malling=malling)


@dp.message_handler(user_id=admin_id, state=NewMalling.Photo, content_types=ContentType.PHOTO)
async def add_malling_photo(message: types.Message, state: FSMContext):
    malling_photo = message.photo[-1].file_id
    data = await state.get_data()
    malling: Malling = data.get("malling")
    malling.malling_photo = malling_photo
    chat_id = message.from_user.id

    text = ("Название: {malling_name}"
                  '\nПришлите цену товара или нажмите "Отмена"')

    await bot.send_photo(chat_id,
        malling_photo,
        caption=text.format(malling_name=malling.malling_name))

    await NewMalling.Price.set()
    await state.update_data(malling=malling)


@dp.message_handler(user_id=admin_id, state=NewMalling.Price)
async def enter_malling_price(message: types.Message, state: FSMContext):
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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")]
        ]
    )
    await message.answer(("Цена: {malling_price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить').format(malling_price=malling_price), 
                         reply_markup=markup)
    await state.update_data(malling=malling)
    await NewMalling.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewMalling.Confirm)
async def enter_malling_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите цену товара заново")
    await NewMalling.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewMalling.Confirm)
async def enter_malling_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    malling: Malling = data.get("malling")
    await malling.create()
    await call.message.answer("Товар успешно создан.")
    await state.reset_state()


@dp.callback_query_handler(user_id=admin_id, text_contains="add_pants")
async def add_pants_item(call: CallbackQuery):
    chat_id = call.from_user.id
    text = ("Введите название товара или нажмите:")
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await bot.send_message(chat_id, text, reply_markup=button)
    await NewPants.Name.set()

@dp.message_handler(user_id=admin_id, state=NewPants.Name)
async def enter_pants_name(message: types.Message, state: FSMContext):
    pants_name = message.text
    pants = Pants()
    pants.pants_name = pants_name
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await message.answer(("Название: {pants_name}"
                           '\nПришлите фотографию товара (не документ) или нажмите "Отмена"').format(pants_name=pants_name),
                           reply_markup=button)

    await NewPants.Photo.set()
    await state.update_data(pants=pants)


@dp.message_handler(user_id=admin_id, state=NewPants.Photo, content_types=ContentType.PHOTO)
async def add_pants_photo(message: types.Message, state: FSMContext):
    pants_photo = message.photo[-1].file_id
    data = await state.get_data()
    pants: Pants = data.get("pants")
    pants.pants_photo = pants_photo
    text = ("Название: {pants_name}"
                  '\nПришлите мне цену товара или нажмите "Отмена"')
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    chat_id = message.from_user.id

    await bot.send_photo(chat_id, pants_photo,
        caption=text.format(pants_name=pants.pants_name),
                  reply_markup=button)

    await NewPants.Price.set()
    await state.update_data(pants=pants)


@dp.message_handler(user_id=admin_id, state=NewPants.Price)
async def enter_pants_price(message: types.Message, state: FSMContext):
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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await message.answer(("Цена: {pants_price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить').format(pants_price=pants_price),
                         reply_markup=markup)
    await state.update_data(pants=pants)
    await NewPants.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewPants.Confirm)
async def enter_pants_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите цену товара заново.")
    await NewPants.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewPants.Confirm)
async def enter_pants_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    pants: Pants = data.get("pants")
    await pants.create()
    await call.message.answer("Товар успешно создан.")
    await state.reset_state()


@dp.callback_query_handler(user_id=admin_id, text_contains="add_shoes")
async def add_shoes(call: CallbackQuery):
    chat_id = call.from_user.id
    text = ("Введите название товара или нажмите:")
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await bot.send_message(chat_id, text, reply_markup=button)
    await NewShoes.Name.set()


@dp.message_handler(user_id=admin_id, state=NewShoes.Name)
async def enter_shoes_name(message: types.Message, state: FSMContext):
    shoes_name = message.text
    shoes = Shoes()
    shoes.shoes_name = shoes_name
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )


    await message.answer(("Название: {shoes_name}"
                           '\nПришлите фотографию товара (не документ) или нажмите "Отмена"').format(shoes_name=shoes_name),
                           reply_markup=button)

    await NewShoes.Photo.set()
    await state.update_data(shoes=shoes)


@dp.message_handler(user_id=admin_id, state=NewShoes.Photo, content_types=ContentType.PHOTO)
async def add_shoes_photo(message: types.Message, state: FSMContext):
    shoes_photo = message.photo[-1].file_id
    data = await state.get_data()
    shoes: Shoes = data.get("shoes")
    shoes.shoes_photo = shoes_photo
    chat_id = message.from_user.id
    text = ("Название: {shoes_name}"
                  "\nПришлите мне цену товара.")

    await bot.send_photo(chat_id,
        shoes_photo,
        caption=text.format(shoes_name=shoes.shoes_name))

    await NewShoes.Price.set()
    await state.update_data(shoes=shoes)


@dp.message_handler(user_id=admin_id, state=NewShoes.Price)
async def enter_shoes_price(message: types.Message, state: FSMContext):
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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await message.answer(("Цена: {shoes_price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить').format(shoes_price=shoes_price),
                         reply_markup=markup)
    await state.update_data(shoes=shoes)
    await NewShoes.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewShoes.Confirm)
async def enter_shoes_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите цену товара заново.")
    await NewShoes.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewShoes.Confirm)
async def enter_shoes_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    shoes: Shoes = data.get("shoes")
    await shoes.create()
    await call.message.answer("Товар успешно создан.")
    await state.reset_state()


@dp.callback_query_handler(user_id=admin_id, text_contains="add_other")
async def add_other(call: CallbackQuery):
    chat_id = call.from_user.id
    text = ("Введите название товара или нажмите:")
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await bot.send_message(chat_id, text, reply_markup=button)
    await NewOther.Name.set()


@dp.message_handler(user_id=admin_id, state=NewOther.Name)
async def enter_other_name(message: types.Message, state: FSMContext):
    other_name = message.text
    other = Other()
    other.other_name = other_name
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await message.answer(("Название: {other_name}"
                           '\nПришлите фотографию товара (не документ) или нажмите "Отмена"').format(other_name=other_name),
                           reply_markup=button)

    await NewOther.Photo.set()
    await state.update_data(other=other)


@dp.message_handler(user_id=admin_id, state=NewOther.Photo, content_types=types.ContentType.PHOTO)
async def add_other_photo(message: types.Message, state: FSMContext):
    other_photo = message.photo[-1].file_id
    data = await state.get_data()
    other: Other = data.get("other")
    text = ("Название: {other_name}"
                  '\nПришлите цену товара или нажмите "Отмена"')
    other.other_photo = other_photo
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    chat_id = message.from_user.id

    await bot.send_photo(chat_id, other_photo,
        caption=text.format(other_name=other.other_name),
                  reply_markup=button)

    await NewOther.Price.set()
    await state.update_data(other=other)


@dp.message_handler(user_id=admin_id, state=NewOther.Price)
async def enter_other_price(message: types.Message, state: FSMContext):
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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await message.answer(("Цена: {other_price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить').format(other_price=other_price),
                         reply_markup=markup)
    await state.update_data(other=other)
    await NewOther.Confirm.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="change", state=NewOther.Confirm)
async def enter_other_price(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Введите заново цену товра")
    await NewOther.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewOther.Confirm)
async def enter_other_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    other: Other = data.get("other")
    await other.create()
    await call.message.answer("Товар успешно создан.")
    await state.reset_state()



# Фича для рассылки по юзерам (учитывая их язык)
@dp.callback_query_handler(user_id=admin_id, text_contains=["mailing"])
async def mailing(call: CallbackQuery):
    await call.message.answer("Пришлите текст рассылки")
    await Mailing.Text.set()

dp.message_handler(user_id=admin_id, state=Mailing.Text)
async def mailing_abc(message: types.Message, state: FSMContext):
    text = message.text
    chat_id = message.from_user.id
    await state.update_data(text=text)
    text = ("Текст:\n {text}\n Уверены?")
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text=("Да"), callback_data="confirm_mall")],
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await bot.send_message(chat_id, text.format(text=text), reply_markup=markup)
    await Mailing.Mall.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm_mall", state=Mailing.Mall)
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
