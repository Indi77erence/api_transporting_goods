from pydantic import BaseModel


class CreateGoods(BaseModel):
	pick_up: int
	delivery: int
	weight: int
	description: str


class GetGoods(BaseModel):
	id: int
	pick_up: int
	delivery: int
	weight: int
	description: str


class GetListGoods(BaseModel):
	pick_up: int
	delivery: int
	car_count: int


class GetGoodsByID(BaseModel):
	pick_up: int
	delivery: int
	weight: int
	description: str
	car_numbers: list[str]


class DataUpdateGoods(BaseModel):
	weight: int = None
	description: str = None


class ErrorResponse(BaseModel):
	error: str


class DeleteGoods(BaseModel):
	status: bool
	message: str
