from pydantic import BaseModel, Field
from typing import Optional, List, Any


class SearchQuery(BaseModel):
    """Схема для поискового запроса"""

    query: str = Field(..., min_length=1, description="Поисковый запрос")
    fields: List[str] = Field(
        default=["title", "content"], description="Поля для поиска"
    )
    size: int = Field(default=10, ge=1, le=100, description="Количество результатов")
    from_: int = Field(
        default=0, ge=0, alias="from", description="Смещение для пагинации"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "query": "Elasticsearch tutorial",
                "fields": ["title", "content", "id"],
                "size": 5,
                "from": 0,
            }
        }


class SearchHit(BaseModel):
    """Один результат поиска"""

    id: str
    score: float
    source: dict[str, Any]


class SearchResponse(BaseModel):
    """Ответ с результатами поиска"""

    total: int
    max_score: Optional[float]
    hits: List[SearchHit]
    took: int  # время выполнения в мс
