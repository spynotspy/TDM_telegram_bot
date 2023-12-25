import json
import shutil
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
from openpyxl import Workbook

tables = create_engine('sqlite:///mystery_santa.db')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    number = Column(String)
    address = Column(String)
    gift_positive = Column(String)
    gift_negative = Column(String)


class Courier(Base):
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    number = Column(String)
    is_available = Column(Boolean)
    delivery_status = Column(String)


Base.metadata.create_all(tables)

Session = sessionmaker(bind=tables)
session = Session()


def add_user(message):
    user = session.query(User).filter_by(id=message.chat.id).first()
    if not user:
        new_user = User(id=message.chat.id, name="name", number="number", address="address",
                        gift_positive="positive_gift",
                        gift_negative="negative_gift")
        session.add(new_user)
        session.commit()
    else:
        return False


def add_username(message):
    user = session.query(User).filter_by(id=message.chat.id).first()
    if user:
        user.name = message.text
        session.commit()


def add_user_number(message):
    user = session.query(User).filter_by(id=message.chat.id).first()
    if user:
        user.number = message.text
        session.commit()


def add_address(message):
    user = session.query(User).filter_by(id=message.chat.id).first()
    if user:
        user.address = message.text
        session.commit()


def add_positive_gift(message):
    user = session.query(User).filter_by(id=message.chat.id).first()
    if user:
        user.gift_positive = message.text
        session.commit()


def add_negative_gift(message):
    user = session.query(User).filter_by(id=message.chat.id).first()
    if user:
        user.gift_negative = message.text
        session.commit()


def add_courier(message):
    courier = session.query(Courier).filter_by(id=message.chat.id).first()
    if not courier:
        new_courier = Courier(id=message.chat.id, name="name", number="number", is_available=True,
                              delivery_status="Ожидает")
        session.add(new_courier)
        session.commit()
    else:
        return False


def add_courier_name(message):
    user = session.query(Courier).filter_by(id=message.chat.id).first()
    if user:
        user.name = message.text
        session.commit()


def add_courier_numb(message):
    user = session.query(Courier).filter_by(id=message.chat.id).first()
    if user:
        user.number = message.text
        session.commit()


def retrieve_and_return_names():
    user_names = [user.name for user in session.query(User).all()]
    courier_names = [courier.name for courier in session.query(Courier).all()]

    return user_names, courier_names


def get_users_id():
    user_ids = [user.id for user in session.query(User).all()]
    return user_ids


def get_user_data(user_id):
    user_name = [user.name for user in session.query(User).filter_by(id=user_id)]
    user_number = [user.number for user in session.query(User).filter_by(id=user_id)]
    user_address = [user.address for user in session.query(User).filter_by(id=user_id)]
    user_gift_positive = [user.gift_positive for user in session.query(User).filter_by(id=user_id)]
    user_gift_negative = [user.gift_negative for user in session.query(User).filter_by(id=user_id)]

    info = [user_name, user_number, user_address, user_gift_positive, user_gift_negative]

    return info


def export_data_to_json():
    users = session.query(User).all()
    data_users = {'users': []}
    for user in users:
        data_users['users'].append({
            'id': user.id,
            'name': user.name,
            'number': user.number,
            'address': user.address,
            'gift_positive': user.gift_positive,
            'gift_negative': user.gift_negative
        })

    couriers = session.query(Courier).all()
    data_couriers = {'couriers': []}
    for courier in couriers:
        data_couriers['couriers'].append({
            'id': courier.id,
            'name': courier.name,
            'number': courier.number,
            'is_available': courier.is_available,
            'delivery_status': courier.delivery_status
        })

    # Объединяем данные в один словарь
    data = {'users': data_users['users'], 'couriers': data_couriers['couriers']}

    # Записываем объединенные данные в JSON-файл
    with open('users_data.json', 'w') as f:
        json.dump(data, f, indent=4)


def export_data_to_xlsx():
    users = session.query(User).all()
    data_users = {
        'id': [],
        'name': [],
        'number': [],
        'address': [],
        'gift_positive': [],
        'gift_negative': []
    }
    for user in users:
        data_users['id'].append(user.id)
        data_users['name'].append(user.name)
        data_users['number'].append(user.number)
        data_users['address'].append(user.address)
        data_users['gift_positive'].append(user.gift_positive)
        data_users['gift_negative'].append(user.gift_negative)

    couriers = session.query(Courier).all()
    data_couriers = {
        'id': [],
        'name': [],
        'number': [],
        'is_available': [],
        'delivery_status': []
    }
    for courier in couriers:
        data_couriers['id'].append(courier.id)
        data_couriers['name'].append(courier.name)
        data_couriers['number'].append(courier.number)
        data_couriers['is_available'].append(courier.is_available)
        data_couriers['delivery_status'].append(courier.delivery_status)

    # Создание DataFrame для пользователей и курьеров
    df_users = pd.DataFrame(data_users)
    df_couriers = pd.DataFrame(data_couriers)

    # Запись данных в Excel файл
    with pd.ExcelWriter('users_data.xlsx') as writer:
        df_users.to_excel(writer, sheet_name='Users', index=False)
        df_couriers.to_excel(writer, sheet_name='Couriers', index=False)


def check_user(desired_id):
    is_courier = session.query(Courier).filter_by(id=desired_id).first()
    if is_courier:  # если user зарегистирован еще и как курьер, то возвращает истину, иначе ложь
        return True

    return False


def check_courier(desired_id):
    is_user = session.query(User).filter_by(id=desired_id).first()
    if is_user:  # если user зарегистирован еще и как курьер, то возвращает истину, иначе ложь
        return True

    return False

# def backup_and_upload_to_google_drive():
#     # Создание объекта GoogleAuth и авторизация
#     gauth = GoogleAuth()
#     gauth.LocalWebserverAuth("470497665018-qvqt7f4gd5eqmohepa48n0b17n7kh68e.apps.googleusercontent.com")
#
#     # Создание объекта GoogleDrive с авторизованным gauth
#     drive = GoogleDrive(gauth)
#
#     # Создание резервной копии базы данных
#     backup_filename = 'mystery_santa_backup.db'
#     shutil.copy('mystery_santa.db', backup_filename)
#
#     # Загрузка резервной копии в Google Drive
#     file1 = drive.CreateFile({'title': backup_filename})
#     file1.SetContentFile(backup_filename)
#     file1.Upload()
#
#     # Удаление локальной резервной копии после загрузки
#     os.remove(backup_filename)

# def create_docx_from_database():
#     # Получение данных из базы данных
#     users = session.query(User).all()
#     couriers = session.query(Courier).all()
#
#     # Создание документа DOCX и добавление данных
#     doc = Document()
#     doc.add_heading('User and Courier Data', level=1)
#
#     # Добавление данных о пользователях
#     doc.add_heading('Users', level=2)
#     for user in users:
#         doc.add_paragraph(
#             f"ID: {user.id}, Name: {user.name}, Number: {user.number}, Address: {user.address}, Gift Positive: {user.gift_positive}, Gift Negative: {user.gift_negative}")
#
#     # Добавление данных о курьерах
#     doc.add_heading('Couriers', level=2)
#     for courier in couriers:
#         doc.add_paragraph(
#             f"ID: {courier.id}, Name: {courier.name}, Number: {courier.number}, Available: {courier.is_available}, Delivery Status: {courier.delivery_status}")
#
#     # Сохранение документа в файл
#     doc.save('users_data')
