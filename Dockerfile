# Dockerfile
FROM python:3.9-slim

# Install dependencies for Postgres, Redis, Poetry
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && pip install --no-cache-dir poetry

# Set workdir
WORKDIR /myspendsheet-backend

COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Expose Django port
EXPOSE 8000

# Set to django lite server (0.0.0.0 bc 127.0.0.1 only allows from self)
CMD ["poetry", "run", "python", "/myspendsheet-backend/myspendsheet/manage.py", "runserver", "0.0.0.0:8000"]