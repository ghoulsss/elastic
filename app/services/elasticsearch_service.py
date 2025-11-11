import uuid

from elasticsearch import Elasticsearch, NotFoundError
from typing import List, Dict, Any, Optional
import logging
from app.config import get_settings
from app.models.document import Document
from app.schemas.search import SearchQuery, SearchResponse, SearchHit

logger = logging.getLogger(__name__)
settings = get_settings()


class ElasticsearchService:
    """Сервис для работы с Elasticsearch"""

    def __init__(self):
        self.client: Optional[Elasticsearch] = None
        self.index_name = settings.default_index

    def connect(self):
        """Подключение к Elasticsearch"""
        if self.client is None:
            self.client = Elasticsearch(
                hosts=["http://localhost:9200"],
                # Дополнительные параметры если нужны:
                # http_auth=('user', 'password'),
                verify_certs=False,
                # ssl_show_warn=False
            )
            logger.info("Connected to Elasticsearch")

    def close(self):
        """Закрытие соединения"""
        if self.client:
            self.client.close()
            logger.info("Elasticsearch connection closed")

    def create_index(self, index_name: Optional[str] = None):
        """Создание индекса с маппингом"""
        index_name = index_name or self.index_name

        body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "created_at": {"type": "date"},
                }
            },
        }

        try:
            if not self.client.ping():
                raise ConnectionError("Elasticsearch is not responding")

            exists = self.client.indices.exists(index=index_name)
            if not exists:
                self.client.indices.create(index=index_name, body=body)
                logger.info(f"Index '{index_name}' created successfully")
            else:
                logger.info(f"Index '{index_name}' already exists")

        except Exception as e:
            logger.error(f"ERROR creating index: {e}")
            raise

    def index_document(
            self,
            document: Document,
            index_name: Optional[str] = None,
    ) -> str:
        """Создание или обновление документа (upsert)"""
        index_name = index_name or self.index_name

        doc_dict = document.model_dump(exclude_unset=True)

        try:
            # Проверяем, существует ли документ
            exists = self.client.exists(index=index_name, id=document.id)

            if exists:
                # Обновляем только изменённые поля
                response = self.client.update(
                    index=index_name,
                    id=document.id,
                    body={
                        "doc": doc_dict,
                        "doc_as_upsert": True
                    }
                )
                logger.info(f"Document {document.id} updated (or created via upsert)")
            else:
                # Создаём новый документ
                response = self.client.index(
                    index=index_name,
                    id=document.id,
                    body=doc_dict,
                )
                logger.info(f"Document {document.id} created")

            return response["_id"]

        except Exception as e:
            logger.error(f"Error indexing/updating document: {e}")
            raise

    def bulk_index(
            self,
            documents: List[Document],
            index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Массовая индексация документов"""
        index_name = index_name or self.index_name

        operations = []
        for doc in documents:
            doc_id = doc.id or str(uuid.uuid4())
            operations.append({"index": {"_index": index_name, "_id": doc_id}})
            operations.append(doc.model_dump(exclude={"id"}))

        try:
            response = self.client.bulk(operations=operations)
            if response["errors"]:
                logger.error(f"Errors in bulk operation: {response['errors']}")
            logger.info(f"Bulk indexed {len(documents)} documents")
            return response
        except Exception as e:
            logger.error(f"Error bulk indexing: {e}")
            raise

    def search(
            self,
            search_query: SearchQuery,
            index_name: Optional[str] = None,
    ) -> SearchResponse:
        """Поиск документов"""
        index_name = index_name or self.index_name

        # Построение запроса
        query_body = {
            "query": {
                "multi_match": {
                    "query": search_query.query,
                    "fields": [f for f in search_query.fields if f != "id"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            },
            "from": search_query.from_,
            "size": search_query.size,
            "track_total_hits": True
        }

        try:
            response = self.client.search(
                index=index_name,
                body=query_body
            )

            # Формирование ответа
            hits = [
                SearchHit(
                    id=hit["_id"],
                    score=hit["_score"],
                    source=hit["_source"]
                )
                for hit in response["hits"]["hits"]
            ]

            return SearchResponse(
                total=response["hits"]["total"]["value"],
                max_score=response["hits"]["max_score"],
                hits=hits,
                took=response["took"],
            )
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise

    def get_document(
            self, doc_id: str, index_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Получение документа по ID"""
        index_name = index_name or self.index_name

        try:
            response = self.client.get(index=index_name, id=doc_id)
            return response["_source"]
        except NotFoundError:
            logger.info(f"Document {doc_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise

    def delete_document(
            self, doc_id: str, index_name: Optional[str] = None
    ) -> bool:
        """Удаление документа"""
        index_name = index_name or self.index_name

        try:
            self.client.delete(index=index_name, id=doc_id)
            logger.info(f"Document {doc_id} deleted")
            return True
        except NotFoundError:
            logger.info(f"Document {doc_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    def update_document(
            self, doc_id: str, updates: Dict[str, Any], index_name: Optional[str] = None
    ) -> bool:
        """Обновление документа"""
        index_name = index_name or self.index_name

        try:
            self.client.update(
                index=index_name,
                id=doc_id,
                body={"doc": updates}
            )
            logger.info(f"Document {doc_id} updated")
            return True
        except NotFoundError:
            logger.info(f"Document {doc_id} not found for update")
            return False
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise

    def delete_index(self, index_name: Optional[str] = None) -> bool:
        """Удаление индекса"""
        index_name = index_name or self.index_name

        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"Index '{index_name}' deleted")
                return True
            else:
                logger.info(f"Index '{index_name}' does not exist")
                return False
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            raise

    def refresh_index(self, index_name: Optional[str] = None):
        """Обновление индекса (делает изменения доступными для поиска)"""
        index_name = index_name or self.index_name

        try:
            self.client.indices.refresh(index=index_name)
            logger.debug(f"Index '{index_name}' refreshed")
        except Exception as e:
            logger.error(f"Error refreshing index: {e}")
            raise


# Singleton instance
es_service = ElasticsearchService()