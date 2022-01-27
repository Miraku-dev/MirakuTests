import asyncio
import datetime
from logging import exception
from admin_panel import item_category

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, InputMediaPhoto, InputMediaVideo, callback_query)
from aiogram.types.input_media import MediaGroup
from aiogram.types.message import ContentType
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null
from aiogram.utils.exceptions import TypeOfFileMismatch

import database
import states
from config import lp_token, admin_id
from load_all import dp, bot
import buttons
import re

db = database.DBCommands()

# Используем CallbackData для работы с коллбеками, в данном случае для работы с покупкой товаров
buy_item = CallbackData("buy", "item_id")
add_to_basket = CallbackData("add", "item_id")


# Для команды /start есть специальный фильтр, который можно тут использовать
@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    count_users = await db.count_users()

    admin_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Список товаров", callback_data="list_categories")],
            [   
                InlineKeyboardButton(text="Наш магазин", callback_data='storage'),
                InlineKeyboardButton(text="Поддержка", callback_data="help")],
            [
                InlineKeyboardButton(text="Корзина", callback_data="basket"),
                InlineKeyboardButton(text="Мои заказы", callback_data="my_orders")
            ],
       ]
    )

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"

    text = ("Привет!\n"
             "\n"
             "Что вы хотите увидеть?")

    if message.from_user.id == admin_id:
        text += ("\n"
                "Сейчас в базе: {count_users} человек(a).\n"
                  "Чтобы увидеть админ-панель нажмите:\n /admin_panel")
    await bot.send_message(chat_id, text.format(count_users=count_users), reply_markup=admin_markup)


@dp.callback_query_handler(text_contains="storage")
async def storage(call: CallbackQuery):
    text = "По этой кнопке мы можем сделать переход на сайт вашего магазина или его страницу в соцсетях."
    await call.answer(text, show_alert=True)


@dp.callback_query_handler(text_contains="help")
async def help(call: CallbackQuery):
    await call.answer(
        "По этой кнопке мы можем сделать переход на поддержку вашего магазина в telegram или любой другой социальной сети.",
    show_alert=True)


@dp.callback_query_handler(text_contains="list_categories")
async def categories_list(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    chat_id = call.from_user.id
    text = "Выберите товар из присутствующих категорий:"
    
    await bot.send_message(chat_id, text, reply_markup=buttons.magic_categories_markup)
    await states.List_item.Item.set()


# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="hats", state=states.List_item.Item)
async def show_hats(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    category = "add_hat"
    all_items = await db.show_hats()
    a = 3
    await state.update_data(a=a)
    await state.update_data(category=category)
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
     
        markup = InlineKeyboardMarkup(
            inline_keyboard=
                [
                    [
                        # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                        InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                    [
                        InlineKeyboardButton(text="Далее", callback_data="next"),
                        InlineKeyboardButton(text="Назад", callback_data="cancel")
                    ],
                    [
                        InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                    ],
                ]
            )
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()


# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="accessories", state=states.List_item.Item)
async def show_accessories(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    all_items = await db.show_accessories()
    # Проходимся по товарам, пронумеровывая
    category = "add_accessories"
    a = 3
    await state.update_data(a=a)
    await state.update_data(category=category)
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")

        markup = InlineKeyboardMarkup(
            inline_keyboard=
                [
                    [
                        # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                        InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                    [
                        InlineKeyboardButton(text="Далее", callback_data="next"),
                        InlineKeyboardButton(text="Назад", callback_data="cancel")
                    ],
                    [
                        InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                    ], 
                ]
            )
        # Отправляем фотку товара с подписью и кнопкой "купить"
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()

# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="malling", state=states.List_item.Item)
async def show_malling(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    all_items = await db.show_malling()
    category = "add_malling"
    a = 3
    await state.update_data(a=a)
    await state.update_data(category=category)
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")

        markup = InlineKeyboardMarkup(
            inline_keyboard=
                [
                    [
                        # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                        InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                    [
                        InlineKeyboardButton(text="Далее", callback_data="next"),
                        InlineKeyboardButton(text="Назад", callback_data="cancel")
                    ],
                    [
                        InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                    ],
                ]
            )
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()


# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="pants", state=states.List_item.Item)
async def show_pants(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    all_items = await db.show_pants()
    category = "add_pants"
    await state.update_data(category=category)
    a = 3
    await state.update_data(a=a)
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")

        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                [
                    InlineKeyboardButton(text="Далее", callback_data="next"),
                    InlineKeyboardButton(text="Назад", callback_data="cancel")
                ],
                [
                    InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                ],
            ]
        )
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()


# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="shoes", state=states.List_item.Item)
async def show_shoes(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    all_items = await db.show_shoes()
    category = "add_shoes"
    a = 3
    await state.update_data(a=a)
    await state.update_data(category=category)
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")

        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                [
                    InlineKeyboardButton(text="Далее", callback_data="next"),
                    InlineKeyboardButton(text="Назад", callback_data="cancel")
                ],
                [
                    InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                ],
            ]
        )
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()


# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="other", state=states.List_item.Item)
async def show_other(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    all_items = await db.show_other()
    category = "add_other"
    await state.update_data(category=category)
    a = 3
    await state.update_data(a=a)
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                [
                    InlineKeyboardButton(text="Далее", callback_data="next"),
                    InlineKeyboardButton(text="Назад", callback_data="cancel")
                ],
                [
                    InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                ],
            ]
        )
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()


@dp.callback_query_handler(text_contains="next", state=states.List_item.Next)
async def show_hats(call: CallbackQuery, state: FSMContext):
    # Достаем товары из базы данных
    data = await state.get_data()
    category = data.get("category")
    a = data.get("a")
    value = a + 3
    await state.update_data(a=value)
    all_items = await database.Item.query.where(database.Item.category == category).offset(a).limit(3).gino.all()
    markup_2 = InlineKeyboardButton(text="Назад", callback_data="cancel")
    if not all_items:
        await call.message.answer("Дальше ничего нет.", reply_markup=markup_2)
        return

    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(item_id=item.id))],
                [
                    InlineKeyboardButton(text="Далее", callback_data="next"),
                    InlineKeyboardButton(text="Назад", callback_data="cancel")
                ],
                [
                    InlineKeyboardButton(text='Добавить в корзину', callback_data=add_to_basket.new(item_id=item.id))
                ],
            ]
        )
        media = MediaGroup()
        if item.photo_1 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_1), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.photo_2 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_2))
        if item.photo_3 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_3))
        if item.photo_4 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_4))
        if item.photo_5 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_5))
        if item.photo_6 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_6))
        if item.photo_7 != None:
            media.attach_photo('{photo}'.format(photo=item.photo_7))
        if item.video_8 != None:
            media.attach_video('{video}'.format(video=item.video_8), text.format(id=item.id,
                        name=item.name,
                        description=item.description,
                        price=item.price / 100))
        if item.video_9 != None:
            media.attach_video('{video}'.format(video=item.video_9))
        await call.message.answer_media_group(media=media)
        await call.message.answer("Выберите действие с помощью кнопок ниже:", reply_markup=markup)
        # Между сообщениями делаем небольшую задержку, чтобы не упереться в лимиты
        await asyncio.sleep(0.3)
        await state.update_data(id=id)
        await states.List_item.Next.set()


@dp.callback_query_handler(add_to_basket.filter(), state=states.List_item.Next)
async def basket_add(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    button = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        InlineKeyboardButton(text="Далее", callback_data="next"),
                        InlineKeyboardButton(text="Назад", callback_data="cancel")
                    ],
                ]
            )

    text = ("Товар добавлен в корзину")
    await call.message.answer(text, reply_markup=button)

    basket = database.Basket()
    basket.item_id = item_id


    await basket.create()
    await states.List_item.Next.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="order_list")
async def order_list(call: CallbackQuery, state: FSMContext):
    all_order = await db.show_order()
    for num, order in enumerate(all_order):
        text = ("Покупатель: {buyer}\n"
                    "id данных в списке: {id}\n"
                    "id товара: {item_id}\n"
                    "Цена товара: {amount}\n"
                    "Количество купленного товара: {quantity}\n"
                    "Время покупки: {purchase_time}\n"
                    "Адрес:\n {shipping_address}\n"
                    "Номер телефона покупателя: {phone_number}\n"
                    "Имя покупателя: {receiver}\n")

        shipping_address = order.shipping_address

        shipping_address = re.sub(r"{", "", str(shipping_address))
        shipping_address = re.sub(r"}", "", str(shipping_address))
        shipping_address = re.sub(r"'", "", str(shipping_address))
        shipping_address = re.sub(r"country_code", "Код страны", str(shipping_address))
        shipping_address = re.sub(r"state", "Область", str(shipping_address))
        shipping_address = re.sub(r"street_line1", "Адрес 1 (улица)", str(shipping_address))
        shipping_address = re.sub(r"street_line2", "Адрес 2 (улица)", str(shipping_address))
        shipping_address = re.sub(r"city", "Город", str(shipping_address))
        shipping_address = re.sub(r"post_code", "Индекс", str(shipping_address))
        shipping_address = re.sub(r",", ",\n", str(shipping_address))


        markup = InlineKeyboardMarkup(
                inline_keyboard=
                [
                    [
                        # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                        InlineKeyboardButton(text=("Удалить информацию"), callback_data="delete_order")
                    ],
                    [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
                ]
            )
        
        await call.message.answer(
                text.format(
                    id=order.id,
                    item_id=order.item_id,
                    buyer=order.buyer,
                    phone_number=order.phone_number,
                    amount=order.amount / 100,
                    quantity=order.quantity,
                    purchase_time=order.purchase_time,
                    receiver=order.receiver,
                    shipping_address=shipping_address
                ),
                reply_markup=markup
            )
        await asyncio.sleep(0.4)

# Для фильтрования по коллбекам можно использовать buy_item.filter()
@dp.callback_query_handler(buy_item.filter(), state='*')
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    # Достаем информацию о товаре из базы данных
    item = await database.Item.get(item_id)
    if not item:
        await call.message.answer("Такого товара не существует", reply_markup=button)
        return

    text = ("Вы хотите купить товар \"<b>{name}</b>\" по цене: <i>{price:,}/шт.</i>\n"
             'Введите количество или нажмите "Отмена"').format(name=item.name,
                                                             price=item.price / 100)
    await call.message.answer(text, reply_markup=button)
    await states.Purchase.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        item=item,
        purchase=database.Purchase(
            item_id=item_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


# Принимаем в этот хендлер только цифры
@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase.EnterQuantity)
async def enter_quantity(message: Message, state: FSMContext):
    # Получаем количество указанного товара
    quantity = int(message.text)
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["purchase"].quantity = quantity
        item = data["item"]
        amount = item.price * quantity
        data["purchase"].amount = amount

    # Создаем кнопки
    agree_button = InlineKeyboardButton(
        text=("Согласен"),
        callback_data="agree"
    )
    change_button = InlineKeyboardButton(
        text=("Ввести количество заново"),
        callback_data="change"
    )
    cancel_button = InlineKeyboardButton(
        text=("Отменить покупку"),
        callback_data="cancel"
    )

    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [agree_button],  # Первый ряд кнопок
            [change_button],  # Второй ряд кнопок
            [cancel_button]  # Третий ряд кнопок
        ]
    )
    await message.answer(
        ("Хорошо, вы хотите купить <i>{quantity}</i> {name} по цене <b>{price:,}/шт.</b>\n\n"
          "Получится <b>{amount:,}</b>. Подтверждаете?").format(
            quantity=quantity,
            name=item.name,
            amount=amount / 100,
            price=item.price / 100
        ),
        reply_markup=markup)
    await states.Purchase.Approval.set()


# То, что не является числом - не попало в предыдущий хендлер и попадает в этот
@dp.message_handler(state=states.Purchase.EnterQuantity)
async def not_quantity(message: Message):
    await message.answer("Неверное значение, введите число")


# Если человек нажал на кнопку Отменить во время покупки - убираем все
@dp.callback_query_handler(text_contains="cancel", state=states.Purchase)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Вы отменили эту покупку")
    await state.reset_state()


# Если человек нажал "ввести заново"
@dp.callback_query_handler(text_contains="change", state=states.Purchase.Approval)
async def approval(call: CallbackQuery):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Введите количество товара заново.")
    await states.Purchase.EnterQuantity.set()


# Если человек нажал "согласен"
@dp.callback_query_handler(text_contains="agree", state=states.Purchase.Approval)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки

    data = await state.get_data()
    purchase: database.Purchase = data.get("purchase")
    item: database.Item = data.get("item")
    # Теперь можно внести данные о покупке в базу данных через .create()
    await purchase.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text=("Хорошо. Оплатите <b>{amount:,}</b> по методу указанному ниже и нажмите "
                                  "на кнопку ниже").format(amount=purchase.amount))
    ################
    # --Ниже выбрать нужные параметры--
    # Пример заполнения можно посмотреть тут https://surik00.gitbooks.io/aiogram-lessons/content/chapter4.html
    # Но прошу обратить внимание, те уроки по старой версии aiogram и давно не обновлялись, так что могут быть
    # несостыковки.
    ################
    currency = "RUB"
    need_name = True
    need_phone_number = True
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=item.name,
                           description=item.name,
                           payload=str(purchase.id),
                           start_parameter=str(purchase.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=item.name, amount=purchase.amount)
                           ],
                           provider_token=lp_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase=purchase)
    await states.Purchase.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase.Payment)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase: database.Purchase = data.get("purchase")
    success = await check_payment(purchase)

    if success:
        await purchase.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address
            else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.finish()
        await bot.send_message(query.from_user.id, ("Спасибо за покупку."))
    else:
        await bot.send_message(query.from_user.id, ("Покупка не была подтверждена, попробуйте позже..."))


@dp.message_handler(content_types=ContentType.ANY)
async def other_echo(message: Message):
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text="Меню", callback_data="cancel")],
            ]
    )
    await message.answer("Не знаю как на это ответить. Если запутались, нажмите кнопку.", reply_markup=button)


async def check_payment(purchase: database.Purchase):
    return True
