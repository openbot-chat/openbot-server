FROM python:3.11 as builder

ENV PYTHONUNBUFFERED 1

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    unzip \
    wget \
    libcurl4 \
    tesseract-ocr

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

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    postgresql-client \
    dnsutils \
    redis-tools \
    iputils-ping \
    tesseract-ocr \
    ffmpeg

RUN pip install --upgrade pip
RUN pip install playwright
RUN python -m playwright install --with-deps chromium

# The Cognitive Services Speech SDK has not been updated to support OpenSSL 3 and instead is still using OpenSSL 1.1.1.
# https://github.com/Azure-Samples/cognitive-services-speech-sdk/issues/1810
WORKDIR /opt
RUN wget -O - https://www.openssl.org/source/openssl-1.1.1u.tar.gz | tar zxf - 
WORKDIR /opt/openssl-1.1.1u
RUN ./config --prefix=/usr/local \
    && make -j $(nproc) \
    && make install_sw install_ssldirs \
    && ldconfig -v \
    && export SSL_CERT_DIR=/etc/ssl/certs

WORKDIR /app
RUN rm -rf /opt/openssl-1.1.1u
ENV SSL_CERT_DIR=/etc/ssl/certs

COPY --from=builder /app/.venv /app/.venv

COPY ./app /app

EXPOSE 5005

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5005"]