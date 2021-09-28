FROM python:3.9

ENV POETRY_VERSION=1.1.8

ENV POETRY_VERSION=1.1.8

RUN apt-get update && pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml pyproject.toml

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

COPY . .

ENTRYPOINT ./start-services.sh