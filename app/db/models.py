from sqlalchemy import Table, Column, String, Float, ForeignKey, SmallInteger, CheckConstraint
from sqlalchemy import Integer

from app.db.database import metadata


locations = Table(
	'locations',
	metadata,
	Column('id', Integer, primary_key=True),
	Column('city', String(30), nullable=False),
	Column('state_name', String(30), nullable=False),
	Column('zip', Integer, nullable=False, unique=True, index=True),
	Column('lat', Float, nullable=False),
	Column('lng', Float, nullable=False)
)

goods = Table(
	'goods',
	metadata,
	Column('id', Integer, primary_key=True),
	Column('pick_up', Integer, ForeignKey('locations.zip'), nullable=False),
	Column('delivery', Integer, ForeignKey('locations.zip'), nullable=False),
	Column('weight', SmallInteger, nullable=False),
	Column('description', String(1000), nullable=True, default="Description"),
	CheckConstraint('weight >= 0 and weight <= 1000', name='chk_weight')
)

delivery_cars = Table(
	'delivery_cars',
	metadata,
	Column('id', Integer, primary_key=True),
	Column('number_car', String, nullable=False, unique=True),
	Column('current_location', Integer, ForeignKey('locations.zip'), default=None, nullable=False),
	Column('carrying', SmallInteger, nullable=False),
	CheckConstraint('carrying >= 0 and carrying <= 1000', name='chk_carrying')
)
