FROM python:3.11-alpine

RUN mkdir '/transporting_goods'

WORKDIR /transporting_goods

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .