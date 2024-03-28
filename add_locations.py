import asyncio
import os
import random
import string

import pandas as pd

from sqlalchemy import insert

from app.db.models import locations, delivery_cars
from app.db.database import async_session_maker


async def insert_locations():
    """

    Функция, которая предварительно загружает локации в БД.

    """
    columns_to_keep = ['city', 'state_name', 'zip', 'lat', 'lng']
    current_dir = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(current_dir, 'uszips.csv')
    df = pd.read_csv(file_path, usecols=columns_to_keep)

    async with async_session_maker() as session:
        for row in df.itertuples(index=False):
            stmt = insert(locations).values(city=row.city, state_name=row.state_name,
                                            zip=row.zip, lat=row.lat, lng=row.lng)
            await session.execute(stmt)
            await session.commit()


async def add_cars():
    current_locations = [601, 602, 603, 606, 610, 611, 612, 616, 617, 622, 623, 624, 627, 631, 636, 637, 638, 641, 646,
                         647]
    random.shuffle(current_locations)

    default_cars = []
    for _ in range(20):
        number_car = ''.join(random.choices(string.digits, k=4)) + random.choice(string.ascii_uppercase)
        carrying = random.randint(0, 1000)
        default_cars.append({
            "number_car": number_car,
            "current_location": current_locations.pop(),
            "carrying": carrying
        })
    async with async_session_maker() as session:
        stmt = insert(delivery_cars).values(default_cars)
        await session.execute(stmt)
        await session.commit()


async def main():
    await insert_locations()
    await add_cars()

if __name__ == "__main__":
    asyncio.run(main())
