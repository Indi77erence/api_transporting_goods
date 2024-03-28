from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.goods.schemas import CreateGoods, GetGoods, GetListGoods, GetGoodsByID, ErrorResponse, DataUpdateGoods, \
	DeleteGoods
from app.api.goods.service import create_new_goods, get_all_list_goods, get_goods_id, update_goods_by_id, \
	delete_goods_by_id
from app.db.database import get_async_session

# Роутер для управления грузами.
router = APIRouter(
	tags=['Goods']
)


# Роутер получения списка всех имеющихся грузов.
@router.get('/goods', response_model=Union[list[GetListGoods], ErrorResponse])
async def get_all_goods(answer=Depends(get_all_list_goods)):
	return answer


# Роутер получения груза по id.
@router.get('/goods/{goods_id}', response_model=Union[GetGoodsByID, ErrorResponse])
async def get_goods_by_id(goods_id: int, session: AsyncSession = Depends(get_async_session)):
	answer = await get_goods_id(goods_id, session)
	return answer


# Роутер создания груза.
@router.post('/goods', response_model=Union[GetGoods, ErrorResponse], status_code=status.HTTP_201_CREATED)
async def create_goods(data_goods: CreateGoods, session: AsyncSession = Depends(get_async_session)):
	answer = await create_new_goods(data_goods, session)
	return answer


# Роутер изменения груза по id.
@router.patch("/goods/{goods_id}", response_model=Union[GetGoods, ErrorResponse])
async def update_goods(goods_id: int, update_values: DataUpdateGoods = None,
					   session: AsyncSession = Depends(get_async_session)):
	answer = await update_goods_by_id(goods_id, update_values, session)
	return answer


# Роутер удаления груза по id.
@router.delete("/goods/{goods_id}", response_model=DeleteGoods)
async def delete_menu(goods_id: int, session: AsyncSession = Depends(get_async_session)):
	answer = await delete_goods_by_id(goods_id, session)
	return answer
