import asyncio
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData
import buttons as bt

import database
import states
from config import lp_token, admin_id
from load_all import dp, bot

db = database.DBCommands()

buy_hat = CallbackData("buy", "item_id")
buy_accessories = CallbackData("buy", "item_id")
buy_pants = CallbackData("buy", "item_id")
buy_shoes = CallbackData("buy", "item_id")
buy_other = CallbackData("buy", "item_id")
buy_malling = CallbackData("buy", "item_id")


@dp.callback_query_handler(text_contains="cancel", state='*')
async def cancel(call: CallbackQuery, state: FSMContext):
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


@dp.message_handler(commands=["menu"], state='*')
async def cancel(message: Message, state: FSMContext):
    await message.edit_reply_markup()
    await state.finish()
    chat_id = message.from_user.id

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

    text = ("Что вы хотите увидеть?.\n")
    if message.from_user.id == admin_id:
        text += ("Чтобы увидеть админ-панель нажмите:\n /admin_panel")
    await bot.send_message(chat_id, text, reply_markup=markup)
    

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
                InlineKeyboardButton(text="Поддержка", callback_data="help")
            ]
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

# Альтернативно можно использовать фильтр text_contains, он улавливает то, что указано в call.data
@dp.callback_query_handler(text_contains="lang")
async def change_language(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем последние 2 символа (например ru)
    lang = call.data[-2:]
    await db.set_language(lang)

    # После того, как мы поменяли язык, в этой функции все еще указан старый, поэтому передаем locale=lang
    await call.message.answer("Ваш язык был изменен", locale=lang)


@dp.message_handler(commands=["referrals"])
async def check_referrals(message: types.Message):
    referrals = await db.check_referrals()
    text = ("Ваши рефералы:\n{referrals}").format(referrals=referrals)
    await message.answer(text)

@dp.callback_query_handler(text_contains="list_categories")
async def categories_list(call: CallbackQuery):
    await call.message.edit_reply_markup()
    chat_id = call.from_user.id
    text = "Выберите товар из присутствующих категорий:"
    
    await bot.send_message(chat_id, text, reply_markup=bt.magic_categories_markup)


@dp.callback_query_handler(text_contains="hats")
async def show_hats_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_item()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{hat_name}</b>\n"
                 "<b>Цена:</b> \t{hat_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_hat.new(item_id=item.id))
                ],
            ]
        )
        hat_photo=item.hat_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(
            photo=hat_photo,
            caption=text.format(
                id=item.id,
                hat_name=item.hat_name,
                hat_price=item.hat_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="accessories")
async def show_accessories_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_items()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{accessories_name}</b>\n"
                 "<b>Цена:</b> \t{accessories_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                "id: \t{id}\n")

        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_accessories.new(item_id=item.id))
                ],
            ]
        )
        accessorires_photo=item.accessories_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            photo=accessorires_photo,
            caption=text.format(
                id=item.id,
                accessories_name=item.accessories_name,
                accessories_price=item.accessories_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.callback_query_handler(text_contains="malling")
async def show_malling_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_items()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{malling_name}</b>\n"
                 "<b>Цена:</b> \t{malling_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
            
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_malling.new(item_id=item.id))
                ],
            ]
        )
        malling_photo=item.malling_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            malling_photo,
            caption=text.format(
                id=item.id,
                malling_name=item.malling_name,
                malling_price=item.malling_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="pants")
async def show_pants_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_items()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{pants_name}</b>\n"
                 "<b>Цена:</b> \t{pants_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_pants.new(item_id=item.id))
                ],
            ]
        )
        pants_photo=item.pants_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            pants_photo,
            caption=text.format(
                id=item.id,
                pants_name=item.pants_name,
                pants_price=item.pants_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="shoes")
async def show_shoes_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_items()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{shoes_name}</b>\n"
                 "<b>Цена:</b> \t{shoes_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_shoes.new(item_id=item.id))
                ],
            ]
        )
        shoes_photo=item.shoes_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            shoes_photo,
            caption=text.format(
                id=item.id,
                shoes_name=item.shoes_name,
                shoes_price=item.shoes_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.callback_query_handler(text_contains="other")
async def show_other_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_items()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, item in enumerate(all_items):
        text = ("\t<b>{other_name}</b>\n"
                 "<b>Цена:</b> \t{other_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_other.new(item_id=item.id))
                ],
            ]
        )
        other_photo=item.other_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            other_photo,
            caption=text.format(
                id=item.id,
                other_name=item.other_name,
                other_price=item.other_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.message_handler()
async def other_echo(message: Message):
    await message.answer("Извините, не знаю что ответить.\n"
                            "Нажмите, чтобы вызвать меню /menu")



