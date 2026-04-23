FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    mysql-connector-python \
    pymongo

RUN useradd -u 1001 -M -s /bin/false app-user

COPY --chown=1001:1001 main.py /app/main.py

USER 1001

EXPOSE 8000