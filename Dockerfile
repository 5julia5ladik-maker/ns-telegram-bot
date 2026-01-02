# Python 3.11 (стабильная версия для python-telegram-bot 20.x)
FROM python:3.11-slim

# Чтобы логи сразу писались в Railway Logs
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Ставим зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Копируем проект
COPY . /app

# Railway запускает worker командой из Procfile
CMD ["python", "bot.py"]
