from pydantic import BaseModel


class GetDeliveryCar(BaseModel):
    id: int
    number_car: str
    current_location: int
    carrying: int


class CreateDeliveryCar(BaseModel):
    number_car: str
    current_location: int
    carrying: int


class ErrorResponse(BaseModel):
    error: str


class DataUpdateCar(BaseModel):
    current_location: int
