from aiogram import types, Bot
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON)
from sqlalchemy import sql

from config import DB_USER, DB_PASS, DB_HOST, DB_NAME

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    language = Column(String(2))
    full_name = Column(String(100))
    username = Column(String(50))
    referral = Column(Integer)
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Item(db.Model):
    __tablename__ = 'items'
    query: sql.Select

    id = Column(Integer, Sequence('item_seq'), primary_key=True)
    name = Column(String(50))
    description = Column(String(500))
    photo = Column(String(250))
    price = Column(Integer)  # Цена в копейках (потом делим на 100)
    category = Column(String(25))

    def __repr__(self):
        return "<Item(id='{}', name='{}', description='{}', price='{}', category='{}')>".format(
            self.id, self.name, self.description, self.price, self.category)


class Purchase(db.Model):
    __tablename__ = 'purchases'
    query: sql.Select

    id = Column(Integer, Sequence('order_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    item_id = Column(Integer)
    amount = Column(Integer)  # Цена в копейках (потом делим на 100)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

    def __pepr__(self):
        return "<Purchase(id='{}', buyer='{}', item_id='{}', amount='{}', shipping_address='{}', phone_number='{}', receiver='{}', purchase_time='{}', quanity='{}', email='{}')>".format(
            self.id, self.buyer, self.item_id, self.quantity, self.amount, self.shipping_address,
            self.phone_number, self.receiver, self.purchase_time, self.email)

class DBCommands:

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self, referral=None):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name

        if referral:
            new_user.referral = int(referral)
        await new_user.create()
        return new_user

    async def set_language(self, language):
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(language=language).apply()

    async def count_users(self) -> int:
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def check_referrals(self):
        bot = Bot.get_current()
        user_id = types.User.get_current().id

        user = await User.query.where(User.user_id == user_id).gino.first()
        referrals = await User.query.where(User.referral == user.id).gino.all()

        return ", ".join([
            f"{num + 1}. " + (await bot.get_chat(referral.user_id)).get_mention(as_html=True)
            for num, referral in enumerate(referrals)
        ])

    async def show_hats(self):
        category = "add_hat"
        items = await Item.query.where(Item.category == Item.category).limit(5).gino.all()

        return items

    async def show_accessories(self):
        category = "add_accessories"
        items = await Item.query.where(Item.category == category).limit(5).gino.all()

        return items
    
    async def show_malling(self):
        category = "add_malling"
        items = await Item.query.where(Item.category == category).limit(5).gino.all()

        return items

    async def show_pants(self):
        category = "add_pants"
        items = await Item.query.where(Item.category == category).limit(5).gino.all()

        return items

    async def show_shoes(self):
        category = "add_shoes"
        items = await Item.query.where(Item.category == category).limit(5).gino.all()

        return items

    async def show_other(self):
        category = "add_other"
        items = await Item.query.where(Item.category == category).limit(5).gino.all()

        return items

    async def show_order(self):
        order = await Purchase.query.gino.all()

        return order



async def create_db():
    await db.set_bind(f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')

    # Create tables
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()
