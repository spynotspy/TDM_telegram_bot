import asyncio
import logging
import json
import random

from aiogram import Bot, types, Dispatcher, F, Router
from aiogram.dispatcher import router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputFile, FSInputFile

from keyboards import admin_kb, user_kb, user_kb_edit, courier_kb_edit, help_kb_user_only, help_kb_courier_only
from database import add_user, add_username, add_user_number, add_address, add_positive_gift, add_negative_gift, \
    add_courier, add_courier_name, add_courier_numb, retrieve_and_return_names, export_data_to_json, \
    export_data_to_xlsx, check_user, check_courier, get_users_id, get_user_data_by_id, get_users_data_for_couriers

from TOKENS import ADMIN_ID, BOT_TOKEN
from backup import upload_on_disk

router = Router()

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

commands = {'/start': 'Нажмите для запуска бота', '/help': 'Нажмите для просмотра доступных команд',
            '/json': 'Нажмите для экспорта данных в JSON файл'}


async def on_startup(_):
    print("bot online")


####################################__РЕГИСТРАЦИЯ УЧАСТНИКА__####################################################

class user_reg(StatesGroup):
    name = State()
    numb = State()
    address = State()
    gift_positive = State()
    gift_negative = State()


@dp.message(Command("json"))
async def export_data_json(message: types.Message):
    export_data_to_json()

    file_input = FSInputFile('users_data.json')
    await bot.send_document(message.chat.id, file_input, caption='Данные о всех курьерах и участниках')


@dp.message(Command("xlcx"))
async def export_data_docx(message: types.Message):
    export_data_to_xlsx()

    file_input = FSInputFile('users_data.xlsx')
    await bot.send_document(message.chat.id, document=file_input, caption='Данные о всех курьерах и участниках')


@dp.callback_query(F.data == "members" or Command("members"))
async def send_members_list(call: types.CallbackQuery):
    user_names, courier_names = retrieve_and_return_names()
    user_names_text = "\n".join(user_names)
    courier_names_text = "\n".join(courier_names)
    await call.message.answer(f"Список игроков:\n{user_names_text}")
    await call.message.answer(f"Список курьеров:\n{courier_names_text}")


@dp.callback_query(F.data == "reg")
async def start_registration(call: types.CallbackQuery, state=FSMContext):
    if check_user(call.message.chat.id):
        await call.message.answer("Вы уже зарегистированы как курьер.")
        await state.clear()
    else:
        add_user(call.message)
        await call.message.answer(f"Введите свое имя: ")
        await state.set_state(user_reg.name)


@dp.message(user_reg.name)
async def add_name(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(name=message.text)
    add_username(message)
    await bot.send_message(chat_id, "Отлично! Теперь отправьте ваш номер телефона:")
    await state.set_state(user_reg.numb)


@dp.message(user_reg.numb)
async def add_name(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(numb=message.text)
    add_user_number(message)
    await bot.send_message(chat_id,
                           "Напишите свой адрес проживания.\n Обязательно перепроверьте, иначе подарок может получить кто-то другой с:")
    await state.set_state(user_reg.address)


@dp.message(user_reg.address)
async def add_numb(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(address=message.text)
    add_address(message)
    await bot.send_message(chat_id,
                           "Теперь самое приятное: напишите пожелания к своему подарку, т.е что бы вы хотели получить")
    await state.set_state(user_reg.gift_positive)


@dp.message(user_reg.gift_positive)
async def add_name(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(gift_positive=message.text)
    add_positive_gift(message)
    await bot.send_message(chat_id, "Напишите то, что вы точно не хотите видеть в качестве подарка:")
    await state.set_state(user_reg.gift_negative)


@dp.message(user_reg.gift_negative)
async def add_name(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(gift_negative=message.text)
    add_negative_gift(message)
    await bot.send_message(chat_id, "Регистрация окончена! Ожидайте начала жеребьёвки.\n"
                                    "P.S: Если захочешь обновить какие-то свои данные - зарегистрируйся заново",
                           reply_markup=user_kb_edit.as_markup())
    await state.clear()
    upload_on_disk()


################################################################################################

###################################__Регистрация курьера__#############################################################
class courier_reg(StatesGroup):
    name = State()
    numb = State()
    is_available = State()
    delivery_status = State()


@dp.callback_query(F.data == "courier")
async def start_registration(call: types.CallbackQuery, state=FSMContext):
    if check_courier(call.message.chat.id):
        await call.message.answer("Вы уже зарегистрированы")
        await state.clear()
    else:
        add_courier(call.message)
        await call.message.answer(f"Введите свое имя: ")
        await state.set_state(courier_reg.name)


@dp.message(courier_reg.name)
async def add_name_courier(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(name=message.text)
    add_courier_name(message)
    await bot.send_message(chat_id, "Отлично! Теперь отправьте ваш номер телефона:")
    await state.set_state(courier_reg.numb)


@dp.message(courier_reg.numb)
async def add_numb_courier(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    await state.update_data(numb=message.text)
    add_courier_numb(message)
    await bot.send_message(chat_id,
                           "Зарегистрировали. Ожидайте, с вами свяжутся!\n"
                           "P.S: Если хотите обновить свои данные - нажмите кнопку ниже",
                           reply_markup=courier_kb_edit.as_markup())
    await state.clear()
    upload_on_disk()

    # await state.set_state(courier_reg.is_available)


################################################################################################

@dp.callback_query(F.data == "data_for_couriers")
async def members_list_for_couriers(call: types.CallbackQuery):
    names, numbers, addresses = get_users_data_for_couriers()
    for i in range(len(names)):
        await call.message.answer(f"Имя: {names[i]}, Номер: {numbers[i]}, Адрес: {addresses[i]}")


@dp.message(Command("help"))
async def help_command(message: types.Message):
    if check_courier(message.chat.id):
        await message.answer("Вот, потыкайте тут", reply_markup=help_kb_user_only.as_markup())
    if check_user(message.chat.id):
        await message.answer("Вот, потыкайте тут. Для курьеров", reply_markup=help_kb_courier_only.as_markup())


@dp.message(StateFilter(None), Command("start"))
async def start_command(message: types.Message, state=FSMContext):
    chat_id = message.chat.id
    if (chat_id == ADMIN_ID):
        await bot.send_message(chat_id, "Привет👋! Ты - организатор ТДМа, а значит тебе назначать жеребъевку\n"
                                        "Если хочешь участвовать тоже - нажми на кнопку 'Регистрация'.\n"
                                        "Если хочешь начать жеребьевку - нажми на кнопку 'Жеребьевка'.\n"
                                        "Посмотреть список зарегистрированных участников - 'Список участников'.\n",
                               reply_markup=admin_kb.as_markup())

    else:
        await bot.send_message(chat_id, "Привет👋! Выбери роль для участия.\n"
                                        "Курьеры - они доставляют подарки адресатам, сами в игре не участвуют, в отличие от игроков\n",
                               reply_markup=user_kb.as_markup())


@dp.callback_query(F.data == "draw")
async def draw(message: types.Message):
    users = get_users_id()
    users_copy = users

    random.shuffle(users_copy)
    while (users_copy[-1] == users_copy[0]):
        random.shuffle(users_copy)

    # Создаем словарь, в котором ключами будут ID пользователей, а значениями - их уникальные "пары"
    pairs = {users_copy[i]: users_copy[i + 1] for i in range(len(users_copy) - 1)}
    pairs[users_copy[-1]] = users_copy[0]  # Последний элемент списка парируется с первым

    for user_id, recipient_id in pairs.items():
        recipient_info = get_user_data_by_id(recipient_id)
        await bot.send_message(user_id, f"Твой подопечный - пользователь  {recipient_info[0]}\n"
                                        f"Его номер - {recipient_info[1]}\n"
                                        f"Его адрес - {recipient_info[2]}\n"
                                        f"То, что он хотел бы получить - {recipient_info[3]}\n"
                                        f"То, что ему точно не стоит дарить - {recipient_info[4]}\n")
    upload_on_disk()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
