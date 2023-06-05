FROM python:3.11

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/
