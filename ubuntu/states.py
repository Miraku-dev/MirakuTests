from aiogram.dispatcher.filters.state import StatesGroup, State


class Purchase(StatesGroup):
    EnterQuantity = State()
    Approval = State()
    Payment = State()


class NewHats(StatesGroup):
    Categories= State()
    Name = State()
    Photo = State()
    Price = State()
    Confirm = State()

class NewAccessories(StatesGroup):
    Categories= State()
    Name = State()
    Photo = State()
    Price = State()
    Confirm = State()

class NewPants(StatesGroup):
    Categories= State()
    Name = State()
    Photo = State()
    Price = State()
    Confirm = State()

class NewShoes(StatesGroup):
    Categories= State()
    Name = State()
    Photo = State()
    Price = State()
    Confirm = State()

class NewOther(StatesGroup):
    Categories= State()
    Name = State()
    Photo = State()
    Price = State()
    Confirm = State()

class NewMalling(StatesGroup):
    Categories= State()
    Name = State()
    Photo = State()
    Price = State()
    Confirm = State()


class Mailing(StatesGroup):
    Text = State()
    Mall = State()
