import asyncio
import datetime
from os import access

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
from handlers import buy_malling, buy_pants, buy_accessories, buy_hat, buy_other, buy_shoes


@dp.callback_query_handler(buy_hat.filter())
async def buying_hat_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    hat_id = int(callback_data.get("hat_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    hats = await database.Hats.get(hat_id)
    if not hats:
        await call.message.answer("Такого товара не существует")
        return

    text = ("Вы хотите купить товар \"<b>{hat_name}</b>\" по цене: <i>{hat_price:,}/шт.</i>\n"
             "Введите количество или нажмите отмена").format(hat_name=hats.hat_name,
                                                             hat_price=hats.hat_price)
    await call.message.answer(text)
    await states.Purchase_hats.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        hats=hats,
        purchase_hats=database.Purchase_hats(
            hat_id=hat_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


# Принимаем в этот хендлер только цифры
@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase_hats.EnterQuantity)
async def enter_quantity(message: Message, state: FSMContext):
    # Получаем количество указанного товара
    quantity = int(message.text)
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["purchase_hats"].quantity = quantity
        hats = data["hats"]
        amount = hats.hat_price * quantity
        data["purchase_hats"].amount = amount

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
        ("Хорошо, вы хотите купить <i>{quantity}</i> {hat_name} по цене <b>{hat_price:,}/шт.</b>\n\n"
          "Получится <b>{amount:,}</b>. Подтверждаете?").format(
            quantity=quantity,
            hat_name=hats.hat_name,
            amount=amount,
            hat_price=hats.hat_price
        ),
        reply_markup=markup)
    await states.Purchase_hats.Approval.set()


# То, что не является числом - не попало в предыдущий хендлер и попадает в этот
@dp.message_handler(state=states.Purchase_hats.EnterQuantity)
async def not_quantity(message: Message):
    await message.answer("Неверное значение, введите число")


# Если человек нажал на кнопку Отменить во время покупки - убираем все
@dp.callback_query_handler(text_contains="cancel", state=states.Purchase_hats)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Вы отменили эту покупку")
    await state.reset_state()


# Если человек нажал "ввести заново"
@dp.callback_query_handler(text_contains="change", state=states.Purchase_hats.Approval)
async def approval(call: CallbackQuery):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Введите количество товара заново.")
    await states.Purchase_hats.EnterQuantity.set()


# Если человек нажал "согласен"
@dp.callback_query_handler(text_contains="agree", state=states.Purchase_hats.Approval)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки

    data = await state.get_data()
    purchase_hats: database.Purchase_hats = data.get("purchase_hats")
    hats: database.Hats = data.get("hats")
    # Теперь можно внести данные о покупке в базу данных через .create()
    await purchase_hats.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text=("Хорошо. Оплатите <b>{amount:,}</b> по методу указанному ниже и нажмите "
                                  "на кнопку ниже").format(amount=purchase_hats.amount))
    ################
    # --Ниже выбрать нужные параметры--
    # Пример заполнения можно посмотреть тут https://surik00.gitbooks.io/aiogram-lessons/content/chapter4.html
    # Но прошу обратить внимание, те уроки по старой версии aiogram и давно не обновлялись, так что могут быть
    # несостыковки.
    ################
    currency = "RUB"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=hats.hat_name,
                           description=hats.hat_name,
                           payload=str(purchase_hats.id),
                           start_parameter=str(purchase_hats.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=hats.hat_name, amount=purchase_hats.amount)
                           ],
                           provider_token=lp_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase_hats=purchase_hats)
    await states.Purchase_hats.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase_hats.Payment)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase_hats: database.Purchase_hats = data.get("purchase_hats")
    success = await check_payment(purchase_hats)

    if success:
        await purchase_hats.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address
            else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(query.from_user.id, ("Спасибо за покупку"))
    else:
        await bot.send_message(query.from_user.id, ("Покупка не была подтверждена, попробуйте позже..."))


async def check_payment(purchase_hats: database.Purchase_hats):
    return True




@dp.callback_query_handler(buy_accessories.filter())
async def buying_accessories_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    accessories_id = int(callback_data.get("accessories_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    accessories = await database.Accessories.get(accessories_id)
    if not accessories:
        await call.message.answer("Такого товара не существует")
        return

    text = ("Вы хотите купить товар \"<b>{accessories_name}</b>\" по цене: <i>{accessories_price:,}/шт.</i>\n"
             "Введите количество или нажмите отмена").format(accessories_name=accessories.accessories_name,
                                                             accessories_price=accessories.accessories_price)
    await call.message.answer(text)
    await states.Purchase_accessories.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        accessories=accessories,
        purchase_accessoriesf=database.Purchase_accessories(
            accessories_id=accessories_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


# Принимаем в этот хендлер только цифры
@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase_accessories.EnterQuantity)
async def enter_accessories_quantity(message: Message, state: FSMContext):
    # Получаем количество указанного товара
    quantity = int(message.text)
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["purchase_accessories"].quantity = quantity
        accessories = data["accessories"]
        amount = accessories.accessories_price * quantity
        data["purchase_accessories"].amount = amount

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
        ("Хорошо, вы хотите купить <i>{quantity}</i> {accessories_name} по цене <b>{accessories_price:,}/шт.</b>\n\n"
          "Получится <b>{amount:,}</b>. Подтверждаете?").format(
            quantity=quantity,
            accessories_name=accessories.accessories_name,
            amount=amount,
            accessories_price=accessories.accessories_price
        ),
        reply_markup=markup)
    await states.Purchase_accessories.Approval.set()


# То, что не является числом - не попало в предыдущий хендлер и попадает в этот
@dp.message_handler(state=states.Purchase_accessories.EnterQuantity)
async def not_accessories_quantity(message: Message):
    await message.answer("Неверное значение, введите число")


# Если человек нажал на кнопку Отменить во время покупки - убираем все
@dp.callback_query_handler(text_contains="cancel", state=states.Purchase_accessories)
async def approval_accessories(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Вы отменили эту покупку")
    await state.reset_state()


# Если человек нажал "ввести заново"
@dp.callback_query_handler(text_contains="change", state=states.Purchase_accessories.Approval)
async def approval_accessories(call: CallbackQuery):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Введите количество товара заново.")
    await states.Purchase_accessories.EnterQuantity.set()


# Если человек нажал "согласен"
@dp.callback_query_handler(text_contains="agree", state=states.Purchase_accessories.Approval)
async def approval_accessories(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки

    data = await state.get_data()
    purchase_accessories: database.Purchase_accessories = data.get("purchase_accessories")
    accessories: database.Accessories = data.get("accessories")
    # Теперь можно внести данные о покупке в базу данных через .create()
    await purchase_accessories.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text=("Хорошо. Оплатите <b>{amount:,}</b> по методу указанному ниже и нажмите "
                                  "на кнопку ниже").format(amount=purchase_accessories.amount))
    ################
    # --Ниже выбрать нужные параметры--
    # Пример заполнения можно посмотреть тут https://surik00.gitbooks.io/aiogram-lessons/content/chapter4.html
    # Но прошу обратить внимание, те уроки по старой версии aiogram и давно не обновлялись, так что могут быть
    # несостыковки.
    ################
    currency = "RUB"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=accessories.accessories_name,
                           description=accessories.accessories_name,
                           payload=str(purchase_accessories.id),
                           start_parameter=str(purchase_accessories.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=accessories.accessories_name, amount=purchase_accessories.amount)
                           ],
                           provider_token=lp_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase_accessories=purchase_accessories)
    await states.Purchase_accessories.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase_accessories.Payment)
async def checkout_accessories(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase_accessories: database.Purchase_accessories = data.get("purchase_accessories")
    success = await check_accessories_payment(purchase_accessories)

    if success:
        await purchase_accessories.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address
            else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(query.from_user.id, ("Спасибо за покупку"))
    else:
        await bot.send_message(query.from_user.id, ("Покупка не была подтверждена, попробуйте позже..."))


async def check_accessories_payment(purchase_accessories: database.Purchase_accessories):
    return True



@dp.callback_query_handler(buy_malling.filter())
async def buying_malling_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    malling_id = int(callback_data.get("malling_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    malling = await database.Malling.get(malling_id)
    if not malling:
        await call.message.answer("Такого товара не существует")
        return

    text = ("Вы хотите купить товар \"<b>{malling_name}</b>\" по цене: <i>{malling_price:,}/шт.</i>\n"
             "Введите количество или нажмите отмена").format(malling_name=malling.malling_name,
                                                             malling_price=malling.malling_price)
    await call.message.answer(text)
    await states.Purchase_malling.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        malling=malling,
        purchase_malling=database.Purchase_malling(
            malling_id=malling_id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


# Принимаем в этот хендлер только цифры
@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase_malling.EnterQuantity)
async def enter_malling_quantity(message: Message, state: FSMContext):
    # Получаем количество указанного товара
    quantity = int(message.text)
    async with state.proxy() as data:  # Работаем с данными из ФСМ
        data["purchase_malling"].quantity = quantity
        malling = data["malling"]
        amount = malling.malling_price * quantity
        data["purchase_malling"].amount = amount

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
        ("Хорошо, вы хотите купить <i>{quantity}</i> {malling_name} по цене <b>{malling_price:,}/шт.</b>\n\n"
          "Получится <b>{amount:,}</b>. Подтверждаете?").format(
            quantity=quantity,
            malling_name=malling.malling_name,
            amount=amount,
            malling_price=malling.malling_price
        ),
        reply_markup=markup)
    await states.Purchase_malling.Approval.set()


@dp.message_handler(state=states.Purchase_malling.EnterQuantity)
async def not_quantity_malling(message: Message):
    await message.answer("Неверное значение, введите число")


# Если человек нажал на кнопку Отменить во время покупки - убираем все
@dp.callback_query_handler(text_contains="cancel", state=states.Purchase_malling)
async def approval_malling(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Вы отменили эту покупку")
    await state.reset_state()


# Если человек нажал "ввести заново"
@dp.callback_query_handler(text_contains="change", state=states.Purchase_malling.Approval)
async def approval_malling(call: CallbackQuery):
    await call.message.edit_reply_markup()  # Убираем кнопки
    await call.message.answer("Введите количество товара заново.")
    await states.Purchase_malling.EnterQuantity.set()


# Если человек нажал "согласен"
@dp.callback_query_handler(text_contains="agree", state=states.Purchase_malling.Approval)
async def approval_malling(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()  # Убираем кнопки

    data = await state.get_data()
    purchase_malling: database.Purchase_malling = data.get("purchase_malling")
    malling: database.Malling = data.get("malling")
    # Теперь можно внести данные о покупке в базу данных через .create()
    await purchase_malling.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text=("Хорошо. Оплатите <b>{amount:,}</b> по методу указанному ниже и нажмите "
                                  "на кнопку ниже").format(amount=purchase_malling.amount))
    ################
    # --Ниже выбрать нужные параметры--
    # Пример заполнения можно посмотреть тут https://surik00.gitbooks.io/aiogram-lessons/content/chapter4.html
    # Но прошу обратить внимание, те уроки по старой версии aiogram и давно не обновлялись, так что могут быть
    # несостыковки.
    ################
    currency = "RUB"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=malling.malling_name,
                           description=malling.malling_name,
                           payload=str(purchase_malling.id),
                           start_parameter=str(purchase_malling.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=malling.malling_name, amount=purchase_malling.amount)
                           ],
                           provider_token=lp_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase_malling=purchase_malling)
    await states.Purchase_malling.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase_malling.Payment)
async def checkout_malling(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase_malling: database.Purchase_malling = data.get("purchase_malling")
    success = await check_malling_payment(purchase_malling)

    if success:
        await purchase_malling.update(
            successful=True,
            shipping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address
            else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(query.from_user.id, ("Спасибо за покупку"))
    else:
        await bot.send_message(query.from_user.id, ("Покупка не была подтверждена, попробуйте позже..."))


async def check_malling_payment(purchase_malling: database.Purchase_malling):
    return True