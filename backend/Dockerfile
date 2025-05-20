FROM python:3.12-slim

# Создаем пользователя и группу с явным UID/GID
RUN groupadd -r appuser -g 1000 && \
    useradd -u 1000 -r -g appuser -s /sbin/nologin -c "Application User" appuser && \
    mkdir -p /storage/photos && \
    chown -R appuser:appuser /storage

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код с правильными правами
COPY --chown=appuser:appuser . .

USER appuser

CMD ["python", "-m", "app.main"]