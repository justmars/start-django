# syntax=docker/dockerfile:1.2
FROM python:3.11-slim-bullseye
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/src
COPY /src .
ARG run_cmd
RUN pip install -r requirements.txt && \
  chmod +x /opt/src/scripts/worker.sh /opt/src/scripts/$run_cmd
