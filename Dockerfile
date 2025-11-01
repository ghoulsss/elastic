FROM python:3.11-slim

WORKDIR /app

# Установка uv
RUN pip install uv

# Копирование зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей через uv
RUN uv pip install --system -r requirements.txt

# Копирование кода приложения
COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
