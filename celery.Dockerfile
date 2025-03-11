FROM python:3.11 as builder

ENV PYTHONUNBUFFERED 1

RUN apt-get install -y --no-install-recommends \
      gcc \
      g++ \
      unzip \
      wget \
      libcurl4

RUN pip install --upgrade pip

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR


FROM python:3.11 AS runtime

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv


COPY ./app /app

WORKDIR /app

EXPOSE 5005

ENTRYPOINT celery -A tasks.celery_worker worker -l info -Q tasks-load-datasource