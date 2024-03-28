from typing import Union

from fastapi import Depends
from geopy.distance import geodesic
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.goods.schemas import CreateGoods, GetGoods, DataUpdateGoods, ErrorResponse, DeleteGoods, GetListGoods, \
	GetGoodsByID
from app.db.models import goods, locations, delivery_cars
from app.db.database import get_async_session


async def get_all_list_goods(session: AsyncSession = Depends(get_async_session)) -> Union[list[GetListGoods], ErrorResponse]:
	"""

	Функция, которая выполняет поиск всех грузов.

	Принимает 1 аргумент:
	- session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.
	Возвращает список объектов класса goods.

	"""
	select_coord_goods = select(goods.c.pick_up, goods.c.delivery, locations.c.lat, locations.c.lng). \
		select_from(goods.join(locations, goods.c.pick_up == locations.c.zip))

	select_coord_cars = select(locations.c.lat, locations.c.lng). \
		select_from(delivery_cars.join(locations, delivery_cars.c.current_location == locations.c.zip))

	result_goods = await session.execute(select_coord_goods)
	result_cars = await session.execute(select_coord_cars)

	goods_with_coordinates = result_goods.fetchall()
	cars_with_coordinates = result_cars.fetchall()
	if not cars_with_coordinates or not goods_with_coordinates:
		return {"error": "Недостаточно данных в БД для ответа, проверьте наличие грузов или автомобилей"}
	answer = await add_info_about_cars(goods_with_coordinates, cars_with_coordinates)

	return answer


async def get_goods_id(goods_id: int, session: AsyncSession) -> Union[GetGoodsByID, ErrorResponse]:
	"""

	Функция, которая выполняет поиск груза по id.

	Принимает 2 аргумент:
	- goods_id - id искомого груза.
	- session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.
	Возвращает объект класса goods.

	"""
	goods_query = select(goods, locations.c.lat, locations.c.lng).join(locations,goods.c.pick_up == locations.c.zip).\
		where(goods.c.id == goods_id)

	select_coord_cars = select(delivery_cars.c.number_car, locations.c.lat, locations.c.lng).select_from(
		delivery_cars.join(locations, delivery_cars.c.current_location == locations.c.zip))

	query_goods = await session.execute(goods_query)
	query_cars = await session.execute(select_coord_cars)

	goods_res = query_goods.fetchone()
	cars_res = query_cars.fetchall()
	if not goods_res or not cars_res:
		return {"error": f"Недостаточно данных в БД для ответа, проверьте наличие грузов или автомобилей"}


	answer = await add_info_about_cars([goods_res], cars_res)

	return answer


async def create_new_goods(data_goods: CreateGoods, session) -> Union[GetGoods, ErrorResponse]:
	"""

	Функция, которая создаёт груз.

	Принимает 2 аргумент:
	- data_goods - schema pydantic c необходимыми атрибутами для создания объекта класса goods.
	- session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.
	Возвращает объект класса goods.

	"""
	try:
		query = insert(goods).values(pick_up=data_goods.pick_up, delivery=data_goods.delivery,
									 weight=data_goods.weight, description=data_goods.description).returning(goods)
		res_query = await session.execute(query)
		answer = res_query.fetchone()
		await session.commit()

		info = GetGoods(id=answer.id, pick_up=answer.pick_up, description=answer.description,
						delivery=answer.delivery, weight=answer.weight)
		return info
	except IntegrityError as e:
		error_message = str(e).split(': ')[2].split('\n')[0]
		error = ErrorResponse(error=error_message)
		return error
	except DBAPIError as e:
		error_message = str(e).split(': ')[1].split("\n")[0]
		error = ErrorResponse(error=error_message)
		return error


async def update_goods_by_id(goods_id: int, update_values: DataUpdateGoods, session: AsyncSession) -> Union[GetGoods, ErrorResponse]:
	"""

	Функция, которая изменяет характеристики груза по его id.

	Принимает 3 аргумент:
	- goods_id - id груза, который необходимо изменить.
	- update_values - schema pydantic c необходимыми атрибутами для создания изменения объекта класса goods.
	- session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.

	Возвращает объект класса goods.

	"""
	stmt = update(goods).where(goods.c.id == goods_id). \
		values(update_values.model_dump(exclude_none=True)).returning(goods)
	result_stmt = await session.execute(stmt)
	result = result_stmt.fetchone()
	if not result:
		return {"error": "Некорректный id груза."}
	await session.commit()
	info = GetGoods(id=result.id, pick_up=result.pick_up, description=result.description,
					delivery=result.delivery, weight=result.weight)
	return info



async def delete_goods_by_id(goods_id: int, session: AsyncSession) -> DeleteGoods:
	"""

	Функция, которая удаляет груз по его id.

	Принимает 2 аргумент:
	- goods_id - id груза, который необходимо удалить.
	- session - экземпляр, который обеспечивает асинхронное взаимодействие с БД.

	Возвращает состояние удаления.

	"""
	stmt = delete(goods).where(goods.c.id == goods_id)
	result = await session.execute(stmt)
	if result.rowcount:
		await session.commit()
		return DeleteGoods(status=True, message=f"Груз c id={goods_id} удален")
	return DeleteGoods(status=False, message=f"Груз c id={goods_id} не удален, проверьте данные.")


async def add_info_about_cars(goods_with_coordinates, cars_with_coordinates) -> Union[GetGoodsByID, GetListGoods]:
	"""

	Функция, которая аккумулирует данные об грузах и автомобилях.

	Принимает 2 аргумент:
	- goods_with_coordinates - список координат грузов.
	- cars_with_coordinates - список координат автомобилей.

	Возвращает GetGoodsByID | GetListGoods.

	"""

	car_info = []
	for goods_coord in goods_with_coordinates:
		goods_lat, goods_lng = goods_coord[-2], goods_coord[-1]
		if len(cars_with_coordinates[0]) > 2:
			car_numbers = [number for number, car_lat, car_lng in cars_with_coordinates if
						   geodesic((goods_lat, goods_lng), (car_lat, car_lng)).miles <= 450]
			car_info = GetGoodsByID(pick_up=goods_coord[1], delivery=goods_coord[2], weight=goods_coord[3],
										 description=goods_coord[4], car_numbers=car_numbers)
			return car_info
		else:
			car_count = sum(
				geodesic((goods_lat, goods_lng), coordinates).miles <= 450 for coordinates in cars_with_coordinates)
			car_info.append(GetListGoods(pick_up=goods_coord[0],
										 delivery=goods_coord[1],
										 car_count=car_count))
	return car_info
