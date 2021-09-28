FROM python:3.9

ENV POETRY_VERSION=1.1.8

ENV POETRY_VERSION=1.1.8

RUN apt-get update && \
    pip install "poetry==$POETRY_VERSION" && \
    useradd -U celery && rm -rf /var/cache/apt && \
    mkdir -p /var/log/celery && chown celery /var/log/celery && \
    mkdir -p /var/run/celery && chown celery /var/run/celery

WORKDIR /app

COPY pyproject.toml pyproject.toml

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

COPY . .

ENTRYPOINT ./start-services.sh