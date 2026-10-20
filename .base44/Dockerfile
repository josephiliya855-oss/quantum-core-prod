# Base44 dev image: runtime + dependencies only.
# Application source is bind-mounted at /app by docker-compose.base44.yml so that
# edits in the sandbox are picked up by Django's auto-reloader without a rebuild.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
