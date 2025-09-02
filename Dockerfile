FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  APP_HOME=/app \
  PORT=8000
WORKDIR $APP_HOME

# системни пакети, нужни за psycopg/алембик и healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential curl netcat-traditional && \
  rm -rf /var/lib/apt/lists/*

# депенденсии
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# копирай app кода и alembic
COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY seeds ./seeds

# healthcheck (очакваме /health да връща 200)
HEALTHCHECK --interval=10s --timeout=3s --retries=6 CMD curl -fsS http://localhost:${PORT}/health || exit 1

# по-сигурно да не сме root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# стартираме FastAPI (пътят към app-а при теб е app/main.py → app = create_app())
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
