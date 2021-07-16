from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, shipping_address
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import ContentType, Message
from aiogram.utils import callback_data

from config import admin_id
from load_all import dp, bot
from states import DeleteOrder, NewItem, Mailing, DeleteItem, available_answers_data
from database import Item, Purchase, User, DBCommands
import buttons

db = DBCommands()


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
                InlineKeyboardButton(text="Сделать рассылку", callback_data="mailing"),
                InlineKeyboardButton(text="Список заказов", callback_data="order_list")],
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
            'Выберите в какую категорию вы хотите добавить товар, или нажмите "Отмена"')
    await bot.send_message(chat_id, text, reply_markup=categories_markup)
    await NewItem.Category.set()


@dp.callback_query_handler(user_id=admin_id, text_contains="order_list")
async def order_list(call: CallbackQuery, state: FSMContext):
    all_order = await db.show_order()
    for num, order in enumerate(all_order):
        text = ("Покупатель: {buyer}\n"
                    "id данных в списке: {order_id}\n"
                    "id товара: {item_id}\n"
                    "Цена товара: {amount}\n"
                    "Количество купленного товара: {quantity}\n"
                    "Время покупки: {purchase_time}\n"
                    "Адрес: {shipping_address}\n"
                    "Номер телефона покупателя: {phone_number}\n"
                    "Имя покупателя: {receiver}\n")

    markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    # Создаем кнопку "купить" и передаем ее айдишник в функцию создания коллбека
                    InlineKeyboardButton(text="Удалить информацию", callback_data="delete_order")
                ],
            ]
        )
    
    await call.message.answer(
            text1=text.format(
                order_id=order.order_id,
                item_id=order.item_id,
                buyer=order.buyer,
                phone_number=order.phone_number,
                amount=order.amount,
                quantity=order.quantity,
                purchase_time=order.purchase_time,
                receiver=order.receiver,
                shipping_address=order.shipping_address
            ),
            reply_markup=markup
        )


@dp.callback_query_handler(user_id=admin_id, text_contains="add_hat", state=NewItem.Category)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    category = "add_hat"
    item.category =  category
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer("Введите название товара или нажмите:", reply_markup=button)
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_accessories", state=NewItem.Category)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    category = "add_accessories"
    item.category = category
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer("Введите название товара или нажмите:", reply_markup=button)
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_pants", state=NewItem.Category)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    category = "add_pants"
    item.category = category
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer("Введите название товара или нажмите:", reply_markup=button)
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_shoes", state=NewItem.Category)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    category = "add_shoes"
    item.category = category
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer("Введите название товара или нажмите:", reply_markup=button)
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_malling", state=NewItem.Category)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    category = "add_malling"
    item.category = category
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer("Введите название товара или нажмите:", reply_markup=button)
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.callback_query_handler(user_id=admin_id, text_contains="add_other", state=NewItem.Category)
async def add_item(call: types.CallbackQuery, state: FSMContext):
    item = Item()
    category = "add_other"
    item.category = category
    button = InlineKeyboardMarkup(
        inline_keyboard= 
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer("Введите название товара или нажмите:", reply_markup=button)
    await NewItem.Name.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Name)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.name = name
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [
                InlineKeyboardButton(text=("Отмена"), callback_data="cancel"),
                InlineKeyboardButton(text=("Без описания"), callback_data="none")],
            ]
    )


    await message.answer("Название: {name}"
                           '\nПришлите описание товара, если хотите чтобы оно оставалось пустым, нажмите на кнопку "Без описания"'.format(name=name), 
                           reply_markup=button)

    await NewItem.Descriotion.set()
    await state.update_data(item=item)

@dp.callback_query_handler(user_id=admin_id, text_contains="none", state=NewItem.Descriotion)
async def enter_description(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get("item")
    none = "none"
    item.description = none
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )
    await call.message.answer('\nПришлите мне фотографию товара (не документ) или нажмите "Отмена"', reply_markup=button)
    await NewItem.Photo.set()
    await state.update_data(item=item)
  

@dp.message_handler(user_id=admin_id, state=NewItem.Descriotion)
async def enter_description(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    item: Item = data.get("item")
    item.description = description
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await message.answer("Описание: {description}"
                            '\nПришлите мне фотографию товара (не документ) или нажмите "Отмена"'.format(description=description),
                            reply_markup=button)
            
    await NewItem.Photo.set()
    await state.update_data(item=item)


@dp.message_handler(user_id=admin_id, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    item.photo = photo
    button = InlineKeyboardMarkup(
        inline_keyboard=
            [
                [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
            ]
    )

    await message.answer_photo(
        photo=photo,
        caption=("Название: {name}"
                  '\nПришлите мне цену товара в копейках или нажмите "Отмена"').format(name=item.name), reply_markup=button)

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
            [InlineKeyboardButton(text=("Отмена"), callback_data="cancel")],
        ]
    )
    await message.answer(("Цена: {price:,}\n"
                           'Подтверждаете? Нажмите "Отмена" чтобы отменить').format(price=price / 100),
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
    await call.message.answer("Товар успешно создан.\nАдмин-панель: /admin_panel", reply_markup=markup)
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
    all_items = await Item.query.where(Item.id == id).gino.all()
    for num, item in enumerate(all_items):
        text = ("\t<b>{name}</b>\n")

        if item.description != "none":
            text += ("{description}\n")
        
        text += ("\n<b>Цена:</b> \t{price:,}\n")

        if message.from_user.id == admin_id:
            text += ("\n"
                  "id: \t{id}\n")

        text += "\n Вы уверены что хотите удалить данный товар?"
        
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
                description=item.description,
                price=item.price / 100
            ),
            reply_markup=markup
        )
    await DeleteItem.Delete.set()

@dp.callback_query_handler(user_id=admin_id, text_contains="delete", state=DeleteItem.Delete)
async def delete_item(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = data.get("id")
    await Item.delete.where(Item.id == id).gino.status()

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
    await call.message.answer("Товар удалён.\nАдмин-панель: /admin_panel", reply_markup=markup)
    
    await state.finish()


@dp.callback_query_handler(user_id=admin_id, text_contains="delete_order")
async def delete_order(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введите id данных в списке")
    await DeleteOrder.Get_order_id.set()
    

@dp.message_handler(user_id=admin_id, state=DeleteOrder.Get_order_id)
async def get_order_id(message: types.Message, state: FSMContext):
    try:
        order_id = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, введите число")
        return
    order = await Purchase.get(order_id)
    if not order:
        await message.answer("Такого товара не существует")
        return
    await state.update_data(order_id=order_id)
    all_order = await db.show_order()
    for num, order in enumerate(all_order):
        text = ("Покупатель: {buyer}\n"
                    "id данных в списке: {order_id}\n"
                    "id товара: {item_id}\n"
                    "Цена товара: {amount}\n"
                    "Количество купленного товара: {quantity}\n"
                    "Время покупки: {purchase_time}\n"
                    "Адрес: {shipping_address}\n"
                    "Номер телефона покупателя: {phone_number}\n"
                    "Имя покупателя: {receiver}\n"
                    "\nВы уверены, что хотите удалить эти данные без возможности возврата?")

    markup = InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(text='Да', callback_data="delete_confirm"),
                    InlineKeyboardButton(text='Нет', callback_data="cancel")
                ],
            ]
        )

    await message.answer(
            text1=text.format(
                item_id=order.item_id,
                buyer=order.buyer,
                phone_number=order.phone_number,
                amount=order.amount,
                quantity=order.quantity,
                purchase_time=order.purchase_time,
                receiver=order.receiver,
                shipping_address=order.shipping_address
            ),
            reply_markup=markup
        )


@dp.callback_query_handler(user_id=admin_id, text_contains="delete_confirm", state=DeleteOrder.Delete_order)
async def delete_item(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data.get("order_id")
    await Purchase.delete.where(Purchase.order_id == order_id).gino.status()
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
    await call.message.answer("Товар удалён.\nАдмин-панель: /admin_panel", reply_markup=markup)
    
    await state.finish()