# Запуск контейнеров (создаёт, если нет)
docker-compose up -d

# Перезапуск с пересборкой образов
docker-compose up -d --build

# Вывод логов в реальном времени
docker-compose logs -f

# Остановка всех контейнеров проекта
docker-compose down

# Остановка + удаление volumes (чтобы полностью очистить данные)
docker-compose down -v