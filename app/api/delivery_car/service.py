import random
import re
import string
from typing import Union

from fastapi import Depends
from sqlalchemy import select, insert, func, exists, update
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.delivery_car.schemas import CreateDeliveryCar, GetDeliveryCar, DataUpdateCar, ErrorResponse
from app.db.models import delivery_cars, locations
from app.db.database import get_async_session


async def get_all_deliv_cars(session: AsyncSession = Depends(get_async_session)) -> list[GetDeliveryCar]:
    """

    Функция, которая выполняет поиск всех автомобилей.

    Принимает 1 аргумент:
    - session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.
    Возвращает список объектов класса delivery_cars.

    """
    stmt = select(delivery_cars)
    rez_query = await session.execute(stmt)
    result = rez_query.fetchall()
    info = [GetDeliveryCar(id=answer.id, number_car=answer.number_car, current_location=answer.current_location,
                           carrying=answer.carrying) for answer in result]
    return info


async def create_new_delivery_car(data_car: CreateDeliveryCar, session) -> Union[GetDeliveryCar, ErrorResponse]:
    """

    Функция, которая создаёт новый автомобиль для доставки груза.

    Принимает 2 аргумент:
    - data_car -A.
    - session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.
    Возвращает объект класса delivery_cars.

    """
    try:
        if not await check_unique_number_format(data_car.number_car):
            data_car.number_car = await generate_unique_number()

        if not data_car.current_location:
            exists_query = select(exists().where(locations.c.zip == data_car.current_location))
            result = await session.execute(exists_query)
            if not result.scalar():
                data_car.current_location = await get_random_zip(session)

        query = insert(delivery_cars).values(number_car=data_car.number_car, current_location=data_car.current_location,
                                             carrying=data_car.carrying).returning(delivery_cars)
        res_query = await session.execute(query)
        answer = res_query.fetchone()
        await session.commit()
        info = GetDeliveryCar(id=answer.id, number_car=answer.number_car, current_location=answer.current_location,
                              carrying=answer.carrying)
        return info
    except exc.IntegrityError as e:
        error_message = str(e).split(': ')[2].split('\n')[0]
        error = ErrorResponse(error=error_message)
        return error
    except exc.DBAPIError as e:
        error_message = str(e).split(': ')[1].split("\n")[0]
        error = ErrorResponse(error=error_message)
        return error


async def update_car_by_id(car_id: int, update_values: DataUpdateCar, session: AsyncSession) -> \
        Union[GetDeliveryCar, ErrorResponse]:
    """

    Функция, которая обновляет данные автомобиля по его id.

    Принимает 3 аргумент:
    - car_id - id автомобиля, характеристики которого необходимо изменить.
    - update_values - schema pydantic c необходимыми атрибутами для изменения объекта класса delivery_cars.
    - session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.
    Возвращает объект класса delivery_cars.

    """
    exists_query = select(exists().where(locations.c.zip == update_values.current_location))
    result = await session.execute(exists_query)
    if not result.scalar():
        return {"error": f"Локации {update_values.current_location} не существует"}
    stmt = update(delivery_cars).where(delivery_cars.c.id == car_id).\
        values(current_location=update_values.current_location).returning(delivery_cars)
    result_stmt = await session.execute(stmt)
    result = result_stmt.fetchone()
    await session.commit()
    rezult_data = GetDeliveryCar(id=result[0], number_car=result[1], current_location=result[2],
                 carrying=result[3])
    return rezult_data


async def generate_unique_number():
    """

    Функция, которая генерирует уникальный номер автомобиля.
    Возвращает unique_number.

    """
    number = random.randint(1000, 9999)
    letter = random.choice(string.ascii_uppercase)
    unique_number = str(number) + letter
    return unique_number


async def get_random_zip(session: AsyncSession):
    """

    Функция, которая рандомно получает локацию из таблицы locations.

    Принимает 1 аргумент:
    - session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.

    Возвращает рандомную локацию (zip).

    """
    query = select(locations.c.zip).order_by(func.random()).limit(1)
    result = await session.execute(query)
    random_zip = result.scalar_one()
    return random_zip


async def check_unique_number_format(unique_number):
    """

    Функция, которая проверяет номера для автомобиля по заданным правилам.

    Принимает 1 аргумент:
    - unique_number - номер автомобиля.

    Возвращает True | False.

    """
    pattern = r'^\d{4}[A-Z]$'

    if re.match(pattern, unique_number):
        return True
    else:
        return False
