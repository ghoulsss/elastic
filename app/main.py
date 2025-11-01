from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.api.routes import router
from app.services.elasticsearch_service import es_service
from app.config import get_settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    try:
        # Startup
        logger.info("Starting application...")

        await es_service.connect()
        logger.info("Connected to Elasticsearch")

        # Проверка доступности
        info = await es_service.client.info()
        logger.info(f"Elasticsearch version: {info['version']['number']}")

        await es_service.create_index("test")
        logger.info("Application started successfully")

    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        # Закрываем соединение при ошибке
        await es_service.close()
        raise  # Пробрасываем ошибку дальше

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await es_service.close()
    logger.info("Application shut down successfully")


app = FastAPI(
    title="Elasticsearch Search API",
    description="FastAPI + Elasticsearch search service",
    version="1.0.0",
    lifespan=lifespan,
)

# Подключение роутов
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Elasticsearch Search API", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        info = await es_service.client.info()
        return {
            "status": "healthy",
            "elasticsearch": {
                "cluster_name": info["cluster_name"],
                "version": info["version"]["number"],
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
