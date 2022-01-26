from aiogram import types
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove)

magic_categories_markup = InlineKeyboardMarkup(
    inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Головные уборы", callback_data="hats")],
            [
                InlineKeyboardButton(text="Аксессуары", callback_data="accessories"),
                InlineKeyboardButton(text="Верхняя одежда", callback_data="malling")],
            [
                InlineKeyboardButton(text="Брюки", callback_data="pants"),
                InlineKeyboardButton(text="Обувь", callback_data="shoes")],
            [
                InlineKeyboardButton(text="Другое", callback_data="other"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel")
            ]
        ]
    )

new_start_markup = InlineKeyboardMarkup(
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