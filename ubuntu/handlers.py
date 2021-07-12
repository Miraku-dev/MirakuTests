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

buy_hat = CallbackData("buy", "hat_id")
buy_accessories = CallbackData("buy", "accessories_id")
buy_pants = CallbackData("buy", "pants_id")
buy_shoes = CallbackData("buy", "shoes_id")
buy_other = CallbackData("buy", "other_id")
buy_malling = CallbackData("buy", "malling_id")


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
    await message.message.edit_reply_markup()
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

    text = ("Действие отменено.\n")
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
    all_items = await db.show_hats()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, hats in enumerate(all_items):
        text = ("\t<b>{hats_name}</b>\n"
                 "<b>Цена:</b> \t{hats_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: hat_\t{hats_id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_hat.new(hat_id=hats.hat_id))
                ],
            ]
        )
        hat_photo=hats.hat_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            hat_photo,
            caption=text.format(
                hats_id=hats.hat_id,
                hats_name=hats.hat_name,
                hats_price=hats.hat_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="accessories")
async def show_accessories_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_accessories()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, accessories in enumerate(all_items):
        text = ("\t<b>{accessories_name}</b>\n"
                 "<b>Цена:</b> \t{accessories_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                "id: access_\t{accessories_id}\n")

        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_accessories.new(accessories_id=accessories.accessories_id))
                ],
            ]
        )
        accessorires_photo=accessories.accessories_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            accessorires_photo,
            caption=text.format(
                accessories_id=accessories.accessories_id,
                accessories_name=accessories.accessories_name,
                accessories_price=accessories.accessories_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.callback_query_handler(text_contains="malling")
async def show_malling_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_malling()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, malling in enumerate(all_items):
        text = ("\t<b>{malling_name}</b>\n"
                 "<b>Цена:</b> \t{malling_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: mall_\t{malling_id}")
            
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_malling.new(malling_id=malling.malling_id))
                ],
            ]
        )
        malling_photo=malling.malling_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            malling_photo,
            caption=text.format(
                malling_id=malling.malling_id,
                malling_name=malling.malling_name,
                malling_price=malling.malling_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="pants")
async def show_pants_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_pants()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, pants in enumerate(all_items):
        text = ("\t<b>{pants_name}</b>\n"
                 "<b>Цена:</b> \t{pants_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: pants_\t{pants_id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_pants.new(pants_id=pants.pants_id))
                ],
            ]
        )
        pants_photo=pants.pants_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            pants_photo,
            caption=text.format(
                pants_id=pants.pants_id,
                pants_name=pants.pants_name,
                pants_price=pants.pants_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="shoes")
async def show_shoes_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_shoes()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, shoes in enumerate(all_items):
        text = ("\t<b>{shoes_name}</b>\n"
                 "<b>Цена:</b> \t{shoes_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: shoes_\t{shoes_id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_shoes.new(shoes_id=shoes.shoes_id))
                ],
            ]
        )
        shoes_photo=shoes.shoes_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            shoes_photo,
            caption=text.format(
                shoes_id=shoes.shoes_id,
                shoes_name=shoes.shoes_name,
                shoes_price=shoes.shoes_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.callback_query_handler(text_contains="other")
async def show_other_items(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем товары из базы данных
    all_items = await db.show_other()
    chat_id = call.from_user.id
    # Проходимся по товарам, пронумеровывая
    for num, other in enumerate(all_items):
        text = ("\t<b>{other_name}</b>\n"
                 "<b>Цена:</b> \t{other_price:,}\n")

        if call.from_user.id == admin_id:
            text += ("\n"
                  "id: other_\t{other_id}")
        
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_other.new(other_id=other.other_id))
                ],
            ]
        )
        other_photo=other.other_photo
        # Отправляем фотку товара с подписью и кнопкой "купить"
        await bot.send_photo(chat_id,
            other_photo,
            caption=text.format(
                other_id=other.other_id,
                other_name=other.other_name,
                other_price=other.other_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.message_handler()
async def other_echo(message: Message):
    await message.answer("Извините, не знаю что ответить.\n"
                            "Нажмите, чтобы вызвать меню /menu")



