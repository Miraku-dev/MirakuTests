import asyncio
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery)
from aiogram.utils.callback_data import CallbackData

import database
import states
from config import lp_token, admin_id
from load_all import dp, bot
from states import NewItem

db = database.DBCommands()

# Используем CallbackData для работы с коллбеками, в данном случае для работы с покупкой товаров
buy_item = CallbackData("buy", "item_id")

@dp.callback_query_handler(text_contains="cancel")
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.answer("Действие отменено")
    await state.reset_state()
    chat_id = call.from_user.id
    referral =call.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    count_users = await db.count_users()

    # Отдадим пользователю клавиатуру с выбором языков
    admin_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Список товаров", callback_data="category_list")],
                InlineKeyboardButton(text="Наш магазин", callback_data='storage'),
                InlineKeyboardButton(text="Поддержка", callback_data="help")
        ]
    )

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"

    text = ("Привет!\n"
             "\n"
             "Что вы хотите увидеть?").format(
        count_users=count_users,
        bot_link=bot_link
    )
    if call.from_user.id == admin_id:
        text += ("\n"
                  "Следующее видно только администратору.\n"
                  "Добавить новый товар: /add_item"
                  "Сейчас в базе {count_users} человек!\n").format(count_uesrs=count_users)
    await bot.send_message(chat_id, text, reply_markup=admin_markup)


# Для команды /start есть специальный фильтр, который можно тут использовать
@dp.message_handler(CommandStart())
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    count_users = await db.count_users()

    # Отдадим пользователю клавиатуру с выбором языков
    admin_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Список товаров", callback_data="category_list")],
                InlineKeyboardButton(text="Наш магазин", callback_data='storage'),
                InlineKeyboardButton(text="Поддержка", callback_data="help")
        ]
    )

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"

    text = ("Привет!\n"
             "\n"
             "Что вы хотите увидеть?").format(
        count_users=count_users,
        bot_link=bot_link
    )
    if message.from_user.id == admin_id:
        text += (("\n"
                  "Следующее видит только администратор.\n"
                  "Панель администрации: /admin_panel"
                  "Сейчас в базе {count_users} человек!\n").format(count_uesrs=count_users))
    await bot.send_message(chat_id, text, reply_markup=admin_markup)

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
async def categories(call: CallbackQuery):
    categories_markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Головные уборы", callback_data="hats")],
            [
                InlineKeyboardButton(text="Аксессуары", callback_data="accessories"),
                InlineKeyboardButton(text="Верхняя одежда", callback_data="malling"),
                InlineKeyboardButton(text="Брюки", callback_data="pants"),
                InlineKeyboardButton(text="Обувь", callback_data="shoes"),
                InlineKeyboardButton(text="Другое", calback_data="other"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("Выберите товар из присутствующих категорий:", reply_markup=categories_markup)



@dp.сallback_query_handler(text_contains="hats")
async def show_items(call: CallbackQuery):
    # Достаем товары из базы данных
    all_items = await db.show_hats()
    # Проходимся по товарам, пронумеровывая
    for num, hats in enumerate(all_items):
        text = ("<b>Товар</b> \t№{hats_id}: <u>{hats_name}</u>\n"
                 "<b>Цена:</b> \t{hats_price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(hat_id=hats.hat_id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await call.answer_photo(
            hats_photo=hats.hat_photo,
            caption=text.format(
                hats_id=hats.hat_id,
                hats_name=hats.hat_name,
                hats_price=hats.hat_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="accessories")
async def show_items(call: CallbackQuery):
    # Достаем товары из базы данных
    all_items = await db.show_accessories()
    # Проходимся по товарам, пронумеровывая
    for num, accessories in enumerate(all_items):
        text = ("<b>Товар</b> \t№{accessories_id}: <u>{accessories_name}</u>\n"
                 "<b>Цена:</b> \t{accessories_price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(accessories_id=accessories.accesories_id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await call.answer_photo(
            accessorires_photo=accessories.acessories_photo,
            caption=text.format(
                accessories_id=accessories.accesories_id,
                accessories_name=accessories.accesories_name,
                accessories_price=accessories.accesspries_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="malling")
async def show_items(message: Message):
    # Достаем товары из базы данных
    all_items = await db.show_malling()
    # Проходимся по товарам, пронумеровывая
    for num, malling in enumerate(all_items):
        text = ("<b>Товар</b> \t№{malling_id}: <u>{malling_name}</u>\n"
                 "<b>Цена:</b> \t{malling_price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(malling_id=malling.malling_id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await message.answer_photo(
            malling_photo=malling.malling_photo,
            caption=text.format(
                malling_id=malling.malling_id,
                malling_name=malling.malling_name,
                malling_price=malling.malling_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="pants")
async def show_items(call: CallbackQuery):
    # Достаем товары из базы данных
    all_items = await db.show_pants()
    # Проходимся по товарам, пронумеровывая
    for num, pants in enumerate(all_items):
        text = ("<b>Товар</b> \t№{pants_id}: <u>{pants_name}</u>\n"
                 "<b>Цена:</b> \t{pants_price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(pants_id=pants.pants_id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await call.answer_photo(
            pants_photo=pants.pants_photo,
            caption=text.format(
                pants_id=pants.pants_id,
                pants_name=pants.pants_name,
                pants_price=pants.pants_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



@dp.callback_query_handler(text_contains="shoes")
async def show_items(call: CallbackQuery):
    # Достаем товары из базы данных
    all_items = await db.show_shoes()
    # Проходимся по товарам, пронумеровывая
    for num, shoes in enumerate(all_items):
        text = ("<b>Товар</b> \t№{shoes_id}: <u>{shoes_name}</u>\n"
                 "<b>Цена:</b> \t{shoes_price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(shoes_id=shoes.accesories_id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await call.answer_photo(
            shoes_photo=shoes.shoes_photo,
            caption=text.format(
                shoes_id=shoes.accesories_id,
                shoes_name=shoes.shoes_name,
                shoes_price=shoes.shoes_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)
#######################################

###################################
# Показываем список доступных товаров
@dp.callback_query_handler(text_contains="accessories")
async def show_items(call: CallbackQuery):
    # Достаем товары из базы данных
    all_items = await db.show_other()
    # Проходимся по товарам, пронумеровывая
    for num, other in enumerate(all_items):
        text = ("<b>Товар</b> \t№{other_id}: <u>{other_name}</u>\n"
                 "<b>Цена:</b> \t{other_price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text=("Купить"), callback_data=buy_item.new(other_id=other.other_id))
                ],
            ]
        )

        # Отправляем фотку товара с подписью и кнопкой "купить"
        await call.answer_photo(
            other_photo=other.other_photo,
            caption=text.format(
                other_id=other.other_id,
                other_name=other.other_name,
                other_price=other.other_price
            ),
            reply_markup=markup
        )
        await asyncio.sleep(0.3)



# Для фильтрования по коллбекам можно использовать buy_item.filter()
@dp.callback_query_handler(buy_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    # То, что мы указали в CallbackData попадает в хендлер под callback_data, как словарь, поэтому достаем айдишник
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()

    # Достаем информацию о товаре из базы данных
    item = await database.Item.get(item_id)
    if not item:
        await call.message.answer("Такого товара не существует")
        return

    text = ("Вы хотите купить товар \"<b>{name}</b>\" по цене: <i>{price:,}/шт.</i>\n"
             "Введите количество или нажмите отмена").format(name=item.name,
                                                             price=item.price / 100)
    await call.message.answer(text)
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
    need_phone_number = False
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
        await state.reset_state()
        await bot.send_message(query.from_user.id, ("Спасибо за покупку"))
    else:
        await bot.send_message(query.from_user.id, ("Покупка не была подтверждена, попробуйте позже..."))


@dp.message_handler()
async def other_echo(message: Message):
    await message.answer(message.text)


async def check_payment(purchase: database.Purchase):
    return True
