from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.row(button, button2)

kb2 = InlineKeyboardMarkup(resize_keyboard=True)
b1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
b2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb2.add(b1)
kb2.add(b2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(f'10 x вес(кг) + 6,25 х рост(см) - 5 х возраст(лет) + 5 - для мужчин;\n'
                              f'10 x вес(кг) + 6,25 х рост(см) - 5 х возраст(лет) - 161 - для женщин')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result_m = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    result_w = (10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161)
    await message.answer(f'Ваша норма калорий в сутки:\n'
                         f' {result_m} - для мужчин\n'
                         f' {result_w} - для женщин')
    await UserState.weight.set()
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
