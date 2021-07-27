import logging
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from database import Database

logging.basicConfig(level=logging.INFO)
bot = Bot(token='1905159720:AAGcs1XXnegqWRa3S5MR83tUMLbHEmGoH3o')
db = Database('stud_sovet')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

sign_button = InlineKeyboardButton("Записатись в чергу", callback_data='sign_button')
admin_button = InlineKeyboardButton("Я представник факультету", callback_data='admin_button')
sign_kb = InlineKeyboardMarkup(resize_keyboard=True)
sign_kb.add(sign_button).add(admin_button)


class Form(StatesGroup):
    order_number = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привіт, це бот факультету ХТФ для електронної черги.", reply_markup=sign_kb)


@dp.callback_query_handler(text='sign_button')
async def sign_process(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    info = db.info_about_user('abit', user_id)
    if info is None:
        order = db.get_last_order('abit')['order']
        db.record_prediction('abit', {"user_id": user_id, 'order': order + 1})
        await bot.send_message(callback_query.from_user.id, "По всім організаційним питанням можеш писати голові "
                                                            "студентської ради ХТФ - @alekseymelnik\n\n"
                                                            "Якщо бот не видає тобі номер, пиши розробнику - @kenkpix")
        await bot.send_message(callback_query.from_user.id, f"Твій номер в черзі - {order + 1}")
    else:
        await bot.send_message(callback_query.from_user.id,
                               f"Ти вже записався, твій номер в черзі - {info['order']}")


@dp.callback_query_handler(text='admin_button')
async def admin(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Якщо ти представник факультету, "
                                                        "то ти можеш перевіряти кількість людей в черзі\n"
                                                        "Тисни на /check")


@dp.message_handler(commands=['check'])
async def check_queue(message: types.Message):
    user_id = str(message.from_user.id)
    info = db.info_about_user('abit', user_id)
    if info is not None:
        await message.answer(f"Всього в черзі - {db.get_last_order('abit')['order']}\n\n"
                             f"Твій номер в черзі - {db.info_about_user('abit', user_id)['order']}\n\n"
                             f"Зараз подає документи номер - {db.get_last_order('now')['order']}\n\n"
                             f"Готується до подачі номер - {db.get_last_order('now')['order'] + 1}")
    else:
        await message.answer(f"Всього в черзі зараз - {db.get_last_order('abit')['order']}\n\n"
                             f"Зараз подає документи номер - {db.get_last_order('now')['order']}\n\n"
                             f"Готується до подачі номер - {db.get_last_order('now')['order'] + 1}")


@dp.message_handler(commands=['order'])
async def order(message: types.Message):
    # user_id != '390764405' My id
    user_id = str(message.from_user.id)
    if user_id != '380475715':
        await message.answer("Команда доступна тільки для голови студради ХТФ")
    else:
        await Form.order_number.set()
        await message.answer("Введи номер людини, яка зайшла по черзі")


@dp.message_handler(state=Form.order_number)
async def get_order(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['order'] = int(message.text)

    await message.answer(f"Оновлення: подає документи номер - {data['order']}")
    db.record_prediction('now', {'order': data['order']})
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
