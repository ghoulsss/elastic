1. Создание документа:
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Введение в Elasticsearch",
    "content": "Elasticsearch - это мощная поисковая система на базе Apache Lucene...",
    "category": "tutorial",
    "tags": ["elasticsearch", "search", "python"]
  }'

2. Массовое создание:
  curl -X POST "http://localhost:8000/api/v1/documents/bulk" \
    -H "Content-Type: application/json" \
    -d '[
      {
        "title": "Python async/await",
        "content": "Асинхронное программирование в Python...",
        "category": "tutorial",
        "tags": ["python", "async"]
      },
      {
        "title": "FastAPI best practices",
        "content": "Лучшие практики разработки на FastAPI...",
        "category": "tutorial",
        "tags": ["fastapi", "python"]
      }
    ]'
3. Поиск:
  curl -X POST "http://localhost:8000/api/v1/search" \
    -H "Content-Type: application/json" \
    -d '{
      "query": "elasticsearch python",
      "fields": ["title", "content"],
      "size": 10,
      "category": "tutorial"
    }'
