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
    full_name = Column(String(100))
    username = Column(String(50))
    referral = Column(Integer)
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Hats(db.Model):
    __tablename__ = 'hats'
    query: sql.Select

    hat_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    hat_name = Column(String(50))
    hat_photo = Column(String(250))
    hat_price = Column(Integer)  # Цена в копейках (потом делим на 100)

    def __repr__(self):
        return "<Hats(hat_id='{}', hat_name='{}', hat_price='{}')>".format(
            self.hat_id, self.hat_name, self.hat_price)

class Accessories(db.Model):
    __tablename__ = 'accessories'
    query: sql.Select

    accessories_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    accessories_name = Column(String(50))
    accessories_photo = Column(String(250))
    accessories_price = Column(Integer)  # Цена в копейках (потом делим на 100)

    def __repr__(self):
        return "<Accessories(accessories_id='{}', accessories_name='{}', accessories_price='{}')>".format(
            self.accessories_id, self.accessories_name, self.accessories_price)

class Malling(db.Model):
    __tablename__ = 'malling'
    query: sql.Select

    malling_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    malling_name = Column(String(50))
    malling_photo = Column(String(250))
    malling_price = Column(Integer)  # Цена в копейках (потом делим на 100)

    def __repr__(self):
        return "<Malling(id='{}', name='{}', price='{}')>".format(
            self.malling_id, self.malling_name, self.malling_price)

class Pants(db.Model):
    __tablename__ = 'pants'
    query: sql.Select

    pants_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    pants_name = Column(String(50))
    pants_photo = Column(String(250))
    pants_price = Column(Integer)  # Цена в копейках (потом делим на 100)

    def __repr__(self):
        return "<Pants(pants_id='{}', pants_name='{}', pants_price='{}')>".format(
            self.pants_id, self.pants_name, self.pants_price)

class Shoes(db.Model):
    __tablename__ = 'shoes'
    query: sql.Select

    shoes_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    shoes_name = Column(String(50))
    shoes_photo = Column(String(250))
    shoes_price = Column(Integer)  # Цена в копейках (потом делим на 100)

    def __repr__(self):
        return "<Shoes(shoes_id='{}', shoes_name='{}', shoes_price='{}')>".format(
            self.shoes_id, self.shoes_name, self.shoes_price)

class Other(db.Model):
    __tablename__ = 'other'
    query: sql.Select

    other_id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    other_name = Column(String(50))
    other_photo = Column(String(250))
    other_price = Column(Integer)

    def __repr__(self):
        return "<Other(other_id='{}', other_name='{}', other_price='{}')>".format(
            self.other_id, self.other_name, self.other_price)

#-----------------------

class Purchase_hats(db.Model):
    __tablename__ = 'purchases_hats'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    hat_id = Column(Integer)
    amount = Column(Integer)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

class Purchase_accessories(db.Model):
    __tablename__ = 'purchases_accessories'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    accessories_id = Column(Integer)
    amount = Column(Integer)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

class Purchase_pants(db.Model):
    __tablename__ = 'purchases_pants'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    pants_id = Column(Integer)
    amount = Column(Integer)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

class Purchase_shoes(db.Model):
    __tablename__ = 'purchases_shoes'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    shoes_id = Column(Integer)
    amount = Column(Integer)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

class Purchase_malling(db.Model):
    __tablename__ = 'purchases_malling'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    malling_id = Column(Integer)
    amount = Column(Integer)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

class Purchase_other(db.Model):
    __tablename__ = 'purchases_other'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    other_id = Column(Integer)
    amount = Column(Integer)
    quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    shipping_address = Column(JSON)
    phone_number = Column(String(50))
    email = Column(String(200))
    receiver = Column(String(100))
    successful = Column(Boolean, default=False)

# ---------------------
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

    async def show_accessories(self):
        accessories = await Accessories.query.gino.all()

        return accessories

    async def show_hats(self):
        hats = await Hats.query.gino.all()

        return hats

    async def show_malling(self):
        malling = await Malling.query.gino.all()

        return malling

    async def show_pants(self):
        pants = await Pants.query.gino.all()

        return pants

    async def show_shoes(self):
        shoes = await Shoes.query.gino.all()

        return shoes

    async def show_other(self):
        other = await Other.query.gino.all()

        return other
    

async def create_db():
    await db.set_bind(f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')

    # Create tables
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()
