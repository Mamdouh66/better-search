FROM python:3.11-slim-buster as requirements-stage

WORKDIR /temp

RUN pip install poetry==1.8.3

COPY ./pyproject.toml ./poetry.lock* /temp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim-buster

WORKDIR /app

COPY --from=requirements-stage /temp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

ENV PYTHONPATH=/app