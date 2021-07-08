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
from handlers import buy_malling, buy_pants, buy_accessories, buy_hat, buy_other, buy_shoes


@dp.callback_query_handler(buy_hat.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    hat_id = int(callback_data.get("hat_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    hat_item = await database.Hats.get(hat_id)
    if not hat_item:
        await call.message.answer("Такого товара не существует")
        return

    text = ("Вы хотите купить товар \"<b>{hat_name}</b>\" по цене: <i>{hat_price:,}/шт.</i>\n"
             "Введите количество или нажмите отмена").format(hat_name=hat_item.hat_name,
                                                             hat_price=hat_item.hat_price)
    await call.message.answer(text)
    await states.Purchase_hats.EnterQuantity.set()

    # Сохраняем в ФСМ класс товара и покупки
    await state.update_data(
        hat_item=hat_item,
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
        hat_item = data["hats"]
        amount = hat_item.hat_price * quantity
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
            hat_name=hat_item.hat_name,
            amount=amount,
            hat_price=hat_item.hat_price,
        ),
        reply_markup=markup)
    await states.Purchase_hats.Approval.set()


# То, что не является числом - не попало в предыдущий хендлер и попадает в этот
@dp.message_handler(state=states.Purchase_hats.EnterQuantity)
async def not_quantity(message: Message):
    await message.answer("Неверное значение, введите число")


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
    hat_item: database.Hats = data.get("hats")
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
                           title=hat_item.hat_name,
                           description=hat_item.hat_name,
                           payload=str(purchase_hats.id),
                           start_parameter=str(purchase_hats.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=hat_item.hat_name, amount=purchase_hats.amount)
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


