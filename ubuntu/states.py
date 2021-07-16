from aiogram.dispatcher.filters.state import StatesGroup, State


available_answers_data = ['add_accessories', 'add_hat', 'add_malling', 'add_pants', 'add_shoes', 'add_other']


class Purchase(StatesGroup):
    EnterQuantity = State()
    Approval = State()
    Payment = State()


class NewItem(StatesGroup):
    Category = State()
    Name = State()
    Photo = State()
    Price = State()
    Descriotion = State()
    Confirm = State()


class Mailing(StatesGroup):
    Text = State()
    Mall = State()

class DeleteItem(StatesGroup):
    Get_id = State()
    Delete = State()

class DeleteOrder(StatesGroup):
    Get_order_id = State()
    Delete_order = State()