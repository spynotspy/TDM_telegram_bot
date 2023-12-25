from aiogram import Bot, types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup

# Клавиатура для Админа
admin_kb = InlineKeyboardBuilder()
admin_kb.row(types.InlineKeyboardButton(text="Регистрация", callback_data="reg"))
admin_kb.row(types.InlineKeyboardButton(text="Список участников", callback_data="members"))
admin_kb.add(types.InlineKeyboardButton(text="Курьер", callback_data="courier"))
admin_kb.row(types.InlineKeyboardButton(text="Жеребьевка", callback_data="draw"))

# Клавиатура для пользователя
user_kb = InlineKeyboardBuilder()
user_kb.add(types.InlineKeyboardButton(text="Курьер", callback_data="courier"))
user_kb.add(types.InlineKeyboardButton(text="Игрок", callback_data="reg"))
user_kb.row(types.InlineKeyboardButton(text="Список участников", callback_data="members"))

# клава после регистрации игрока для редактирования
user_kb_edit = InlineKeyboardBuilder()
user_kb_edit.add(types.InlineKeyboardButton(text="Изменить данные", callback_data="reg"))

# клава после регистрации курьера для редактирования
courier_kb_edit = InlineKeyboardBuilder()
courier_kb_edit.add(types.InlineKeyboardButton(text="Изменить данные", callback_data="courier"))

#Клавиатура help
help_kb = InlineKeyboardBuilder()
help_kb.row(types.InlineKeyboardButton(text="Список участников", callback_data="members"))