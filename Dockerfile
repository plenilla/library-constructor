FROM python:3.12.8-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .env .env
# Настраиваем переменные окружения
ENV PYTHONPATH=/app
ENV STATIC_FILES_PATH=/app/frontend/dist

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]