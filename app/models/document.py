from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class Document(BaseModel):
    """Базовая модель документа для индексации"""

    id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    # category: Optional[str] = None
    # tags: list[str] = Field(default_factory=list)
    # metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Введение в Elasticsearch",
                "content": "Elasticsearch - это распределённая поисковая и аналитическая система...",
                # "category": "tutorial",
                # "tags": ["elasticsearch", "search", "python"],
                # "metadata": {"author": "John Doe", "views": 100},
            }
        }
