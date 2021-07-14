from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import admin_id
from load_all import dp, bot
from states import NewItem, Mailing, DeleteItem
from database import Item, User


@dp.message_handler(user_id=admin_id, commands=["cancel"], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили создание товара")
    await state.reset_state()


@dp.message_handler(user_id=admin_id, commands=["add_item"])
async def add_item(message: types.Message):
    await message.answer("Введите название товара или нажмите /cancel")
    await NewItem.Name.set()


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


# Фича для рассылки по юзерам (учитывая их язык)
@dp.message_handler(user_id=admin_id, commands=["tell_everyone"])
async def mailing(message: types.Message):
    await message.answer("Пришлите текст рассылки")
    await Mailing.Text.set()


@dp.message_handler(user_id=admin_id, state=Mailing.Text)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Русский", callback_data="ru")],
            [InlineKeyboardButton(text="English", callback_data="en")],
            [InlineKeyboardButton(text="Україньска", callback_data="uk")],
        ]
    )
    await message.answer(("Пользователям на каком языке разослать это сообщение?\n\n"
                           "Текст:\n"
                           "{text}").format(text=text),
                         reply_markup=markup)
    await Mailing.Language.set()


@dp.callback_query_handler(user_id=admin_id, state=Mailing.Language)
async def mailing_start(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    await state.reset_state()
    await call.message.edit_reply_markup()

    users = await User.query.where(User.language == call.data).gino.all()
    for user in users:
        try:
            await bot.send_message(chat_id=user.user_id,
                                   text=text)
            await sleep(0.3)
        except Exception:
            pass
    await call.message.answer(("Рассылка выполнена."))


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
    all_items = await Item.query.where(Item.id == id).gino.all()
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

@dp.message_handler(user_id=admin_id, text_contains="delete", state=DeleteItem.Delete)
async def delete_item(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    await Item.delete.where(Item.id == id).gino.status()
    await message.answer("Товар удалён.")

