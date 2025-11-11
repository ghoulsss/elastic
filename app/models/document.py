from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class Document(BaseModel):
    """Базовая модель документа для индексации"""

    id: str | int = None
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    # cardID: int = Field()
    # category: Optional[str] = None
    # tags: list[str] = Field(default_factory=list)
    # metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "title": "Введение в Elasticsearch",
                "content": "Elasticsearch - это распределённая поисковая и аналитическая система...",
            }
        }
