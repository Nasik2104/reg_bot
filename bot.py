from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ParseMode
import os
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = "6115025348:AAHu9v0rujd0b_jSeBRc07nYMSeAkeLWKqU"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=str(API_TOKEN))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
storage = MemoryStorage()
dp.storage = storage

inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Реєстрація", callback_data="reg"),
         InlineKeyboardButton(text="Редагування", callback_data="edit")],
        [InlineKeyboardButton(text="Профіль", callback_data="profile")]
    ]
)

async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустити бота'),
        ]
    )
    
async def on_startup(dp):
    await set_default_commands(dp)

class RegistrationState(StatesGroup):
    base = State()
    waiting_for_name = State()  # Встановимо стани для кожного етапу реєстрації
    waiting_for_email = State()
    waiting_for_age = State()
    EditingProfileState = State() 
    EditingProfileState2 = State()

@dp.message_handler(commands=['start'])
async def base(message: types.Message, state=FSMContext):
    await message.answer("Що будемо робити?", reply_markup=inline_kb)
    await RegistrationState.base.set()
    

@dp.callback_query_handler(text="reg", state=RegistrationState.base)
async def cmd_start(call: types.callback_query):
    await call.message.answer("Привіт! Давайте розпочнемо реєстрацію. Введіть ваше ім'я.")
    await RegistrationState.waiting_for_name.set()  

@dp.message_handler(state=RegistrationState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Дякую! Тепер введіть вашу електронну пошту.")
    await RegistrationState.waiting_for_email.set()  


@dp.message_handler(state=RegistrationState.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
    await message.answer("Добре! Введіть ваш вік.")
    await RegistrationState.waiting_for_age.set() 


@dp.message_handler(state=RegistrationState.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
        
        registration_data = {
            'name': data['name'],
            'email': data['email'],
            'age': data['age']
        }
        
        await message.answer(f"Ваша реєстраційна інформація:\n"
                             f"Ім'я: {registration_data['name']}\n"
                             f"Email: {registration_data['email']}\n"
                             f"Вік: {registration_data['age']}",
                             parse_mode=ParseMode.MARKDOWN)
    await RegistrationState.base.set()
    await message.answer("Що будемо робити?", reply_markup=inline_kb)

@dp.callback_query_handler(text="edit", state=RegistrationState.base)
async def edit_profile(call: types.callback_query):
    await RegistrationState.EditingProfileState.set()  
    await call.message.answer("Що ви хочете змінити?\n"
                        "1. Ім'я\n"
                        "2. Email\n"
                        "3. Вік")

@dp.message_handler(lambda message: message.text in ["1", "2", "3"], state=RegistrationState.EditingProfileState)
async def choose_edit_option(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["edit_option"] = message.text  
    await RegistrationState.EditingProfileState2.set()
    await message.reply("Ввдіть нове значення:")

@dp.message_handler(state=RegistrationState.EditingProfileState2)
async def process_new_value(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        edit_option = data["edit_option"]
        if edit_option == "1":
            data["name"] = message.text
        elif edit_option == "2":
            data["email"] = message.text
        elif edit_option == "3":
            data["age"] = message.text
        else:
            pass
    
    async with state.proxy() as data:
        user_info = {
            'name': data['name'],
            'email': data['email'],
            'age': data['age']
        }
        data['user_info'] = user_info  
        await message.answer("Профіль успішно оновлено.")
    registration_data = {
            'name': data['name'],
            'email': data['email'],
            'age': data['age']
        }
        
    await message.answer(f"Ваша змінена інформація:\n"
                             f"Ім'я: {registration_data['name']}\n"
                             f"Email: {registration_data['email']}\n"
                             f"Вік: {registration_data['age']}",
                             parse_mode=ParseMode.MARKDOWN)
    await RegistrationState.base.set()  
    await message.answer("Що будемо робити?", reply_markup=inline_kb)
    
@dp.callback_query_handler(text="profile", state=RegistrationState.base)
async def profile(call: types.CallbackQuery, state=FSMContext):
    async with state.proxy() as data:
        user_info = data['user_info']
        profile_text = (
                f"Ім'я: {user_info['name']}\n"
                f"Email: {user_info['email']}\n"
                f"Вік: {user_info['age']}"
            )
        await call.message.answer(profile_text)
        await RegistrationState.base.set()
        await call.message.answer("Що будемо робити?", reply_markup=inline_kb)
        
        
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
