from fastapi import FastAPI
from app.api.goods.router import router as goods_router
from app.api.delivery_car.router import router as delivery_car_router


def create_app():
	app = FastAPI(title="Api_Transporting_Goods")
	app.include_router(goods_router)
	app.include_router(delivery_car_router)
	return app
