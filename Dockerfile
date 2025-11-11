FROM python:3.11-slim

# Устанавливаем Poetry
RUN pip install poetry

# Создаем рабочую директорию
WORKDIR /app

# Копируем pyproject.toml и устанавливаем зависимости
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root

# Копируем исходный код приложения
COPY app /app/app

# Запускаем FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
