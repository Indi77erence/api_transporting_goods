from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.delivery_car.schemas import GetDeliveryCar, CreateDeliveryCar, ErrorResponse, DataUpdateCar
from app.api.delivery_car.service import get_all_deliv_cars, update_car_by_id, \
	create_new_delivery_car
from app.db.database import get_async_session

# Роутер для управления автомобилями.
router = APIRouter(
	tags=['Delivery_car']
)


# Роутер получения списка всех имеющихся автомобилей.
@router.get('/delivery_cars', response_model=list[GetDeliveryCar])
async def get_all_delivery_cars(answer=Depends(get_all_deliv_cars)):
	return answer


# Роутер создания автомобилей.
@router.post('/delivery_cars', response_model=Union[GetDeliveryCar, ErrorResponse], status_code=status.HTTP_201_CREATED)
async def create_delivery_car(data_delivery_car: CreateDeliveryCar, session: AsyncSession = Depends(get_async_session)):
	answer = await create_new_delivery_car(data_delivery_car, session)
	return answer


# Роутер изменения локации автомобиля.
@router.patch("/delivery_cars/{car_id}", response_model=Union[GetDeliveryCar, ErrorResponse])
async def update_delivery_car(car_id: int, update_values: DataUpdateCar, session: AsyncSession = Depends(get_async_session)):
	answer = await update_car_by_id(car_id, update_values, session)
	return answer
