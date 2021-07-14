from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import admin_id
from load_all import dp, bot
from states import NewItem, Mailing, DeleteItem, available_answers_data
from database import Item, User
import buttons


@dp.callback_query_handler(user_id=admin_id, text_contains="cancel", state='*')
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
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
                InlineKeyboardButton(text="Удалить товар", callback_data="delete_item"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    await message.answer("Что вы хотите сделать?", reply_markup=admin_panel_markup)

@dp.callback_query_handler(user_id=admin_id, text_contains="add_item")
async def item_category(call: types.CallbackQuery):
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
    await NewItem.Start.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="add_hat", state=NewItem.Start)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    if call.message.text.lower() not in available_answers_data:
        await call.message.answer("Выберите ответ, используя кнопки выше.")
        return
    if call.message.text == "add_hat":
        item.category = call.message.text.lower()
        await call.message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_accessories", state=NewItem.Start)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    if call.message.text.lower() not in available_answers_data:
        await call.message.answer("Выберите ответ, используя кнопки выше.")
        return
    if call.message.text == "add_accessories":
        item.category = call.message.text.lower()
        await call.message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_pants", state=NewItem.Start)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    if call.message.text.lower() not in available_answers_data:
        await call.message.answer("Выберите ответ, используя кнопки выше.")
        return
    if call.message.text == "add_pants":
        item.category = call.message.text.lower()
        await call.message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_shoes", state=NewItem.Start)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    if call.message.text.lower() not in available_answers_data:
        await call.message.answer("Выберите ответ, используя кнопки выше.")
        return
    if call.message.text == "add_shoes":
        item.category = call.message.text.lower()
        await call.message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_malling", state=NewItem.Start)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    if call.message.text.lower() not in available_answers_data:
        await call.message.answer("Выберите ответ, используя кнопки выше.")
        return
    if call.message.text == "add_malling":
        item.category = call.message.text.lower()
        await call.message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_other", state=NewItem.Start)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    if call.message.text.lower() not in available_answers_data:
        await call.message.answer("Выберите ответ, используя кнопки выше.")
        return
    if call.message.text == "add_other":
        item.category = call.message.text.lower()
        await call.message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    item: Item = data.get("item")
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
    await call.message.answer(("Введите заново цену товара в копейках"))
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer(("Товар удачно создан."))
    await state.reset_state()


@dp.callback_query_handler(user_id=admin_id, text_contains=["mailing"])
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Пришлите текст рассылки")
    await Mailing.Text.set()

@dp.callback_query_handler(user_id=admin_id, text_contains=["mailing1"], state='*')
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_reply_markup()
    await call.message.answer("Пришлите текст рассылки")
    await Mailing.Text.set()

@dp.message_handler(user_id=admin_id, state=Mailing.Text)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    chat_id = message.from_user.id
    text1 = ("Текст:\n"
                '"{text}"'
             "\n Вы уверены?")
    await state.update_data(text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Да, я уверен(а).", callback_data="none")],
            [InlineKeyboardButton(text="Нет, вернуться к вводу данных", callback_data="mailing1")],
            [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
        ]
    )
    await bot.send_message(chat_id, text1.format(text=text), reply_markup=markup)
    await Mailing.Mall.set()


@dp.callback_query_handler(user_id=admin_id, state=Mailing.Mall)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    await state.reset_state()
    await call.message.edit_reply_markup()

    users = await User.query.gino.all()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id,
                                   text=text)
            await sleep(0.3)
        except Exception:
            pass
    await call.message.answer("Рассылка выполнена. \n Админ-панель: \n/admin_panel", reply_markup=buttons.new_start_markup)


@dp.callback_query_handler(user_id=admin_id, text_contains="delete_item")
async def delete(call: types.CallbackQuery):
    await call.message.answer("Пришлите id товара, который вы хотите удалить.")
    await DeleteItem.Get_id.set()

@dp.message_handler(user_id=admin_id, state=DeleteItem.Get_id)
async def get_id(message: types.Message, state: FSMContext):
    try:
        id = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return
    item = await Item.get(id)
    if not item:
        await message.answer("Такого товара не существует")
        return
    await state.update_data(id=id)
    all_items = await Item.query.where(Item.id == id)
    for num, item in enumerate(all_items):
        text = ("<b>Товар</b> \t№{id}: <u>{name}</u>\n"
                 "<b>Цена:</b> \t{price:,}\n"
                 "\n"
                 "Вы уверены что хотите удалить данный товар?")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text='Да', callback_data="delete"),
                    InlineKeyboardButton(text='Нет', callback_data="cancel")
                ],
            ]
        )

        await message.answer_photo(
            photo=item.photo,
            caption=text.format(
                id=item.id,
                name=item.name,
                price=item.price / 100
            ),
            reply_markup=markup
        )
    await DeleteItem.Delete.set()

@dp.message_handler(user_id=admin_id, state=DeleteItem.Delete)
async def delete_item(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    await Item.delete.where(Item.id == id).gino.status()
    await message.answer("Товар удалён.")

