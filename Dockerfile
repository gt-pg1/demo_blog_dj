FROM python:3.11

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

RUN python blogblog/manage.py collectstatic --no-input --clear

CMD ["gunicorn", "blogblog.wsgi:application", "--bind", "0.0.0.0:8000"]

HEALTHCHECK --interval=5m --timeout=3s CMD curl --fail http://localhost:8000/ || exit 1
