FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    mysql-connector-python \
    pymongo

COPY main.py /app/main.py

EXPOSE 8000