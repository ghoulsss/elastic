from elasticsearch import AsyncElasticsearch, NotFoundError
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
        self.client: Optional[AsyncElasticsearch] = None
        self.index_name = settings.default_index
        # self.index_name = "bdd"

    async def connect(self):
        """Подключение к Elasticsearch"""
        if self.client is None:
            self.client = AsyncElasticsearch(
                hosts=[settings.elasticsearch_host],
                verify_certs=False,
                # basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
            )
            logger.info("Connected to Elasticsearch")

    async def close(self):
        """Закрытие соединения"""
        if self.client:
            await self.client.close()
            logger.info("Elasticsearch connection closed")

    async def create_index(self, index_name: Optional[str] = None):
        """Создание индекса с маппингом"""
        index_name = index_name or self.index_name

        # Маппинг для индекса
        body = {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "created_at": {"type": "date"},
                }
            },
        }

        # settings_config = {
        #     "settings": {"number_of_shards": 1, "number_of_replicas": 0},
        #     "mappings": mappings,
        # }

        try:
            if not await self.client.ping():
                raise ConnectionError("Elasticsearch is not responding")

            exists = await self.client.indices.exists(index=index_name)
            if not exists:
                await self.client.indices.create(index=index_name, **body)
                logger.info(f"Index '{index_name}' created successfully")
            else:
                logger.info(f"Index '{index_name}' already exists")

        except Exception as e:
            print("❌ ERROR creating index:", e)
            if hasattr(e, "info"):
                print("📦 ES error body:", e.info)
            raise

    async def index_document(
        self,
        document: Document,
        index_name: Optional[str] = None,
    ) -> str:
        """Индексация документа"""
        index_name = index_name or self.index_name

        doc_dict = document.model_dump(exclude={"id"})

        try:
            response = await self.client.index(
                index=index_name, id=document.id, document=doc_dict
            )
            logger.info(f"Document indexed with ID: {response['_id']}")
            return response["_id"]
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            raise

    async def bulk_index(
        self,
        documents: List[Document],
        index_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Массовая индексация документов"""
        index_name = index_name or self.index_name

        operations = []
        for doc in documents:
            operations.append({"index": {"_index": index_name}})  # "_id": doc.id
            operations.append(doc.model_dump(exclude={"id"}))

        try:
            response = await self.client.bulk(operations=operations)
            logger.info(f"Bulk indexed {len(documents)} documents")
            return response
        except Exception as e:
            logger.error(f"Error bulk indexing: {e}")
            raise

    async def search(
        self,
        search_query: SearchQuery,
        index_name: Optional[str] = None,
    ) -> SearchResponse:
        """Поиск документов"""
        index_name = index_name or self.index_name

        # Построение запроса
        query = {
            "multi_match": {
                "query": search_query.query,
                "fields": search_query.fields,
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }
        # {
        #     "bool": {
        #         "must": [
        #             {
        #                 "multi_match": {
        #                     "query": search_query.query,
        #                     "fields": search_query.fields,
        #                     "type": "best_fields",
        #                     "fuzziness": "AUTO",
        #                 }
        #             }
        #         ],
        #         "filter": [],
        #     }
        # }

        # # Добавление фильтров
        # if search_query.category:
        #     query["bool"]["filter"].append(
        #         {"term": {"category": search_query.category}}
        #     )

        # if search_query.tags:
        #     query["bool"]["filter"].append({"terms": {"tags": search_query.tags}})

        try:
            response = await self.client.search(
                index=index_name,
                query=query,
                from_=search_query.from_,
                size=search_query.size,
                track_total_hits=True,
            )

            # Формирование ответа
            hits = [
                SearchHit(id=hit["_id"], score=hit["_score"], source=hit["_source"])
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

    async def get_document(
        self, doc_id: str, index_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Получение документа по ID"""
        index_name = index_name or self.index_name

        try:
            response = await self.client.get(index=index_name, id=doc_id)
            return response["_source"]
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise

    async def delete_document(
        self, doc_id: str, index_name: Optional[str] = None
    ) -> bool:
        """Удаление документа"""
        index_name = index_name or self.index_name

        try:
            await self.client.delete(index=index_name, id=doc_id)
            logger.info(f"Document {doc_id} deleted")
            return True
        except NotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    async def update_document(
        self, doc_id: str, updates: Dict[str, Any], index_name: Optional[str] = None
    ) -> bool:
        """Обновление документа"""
        index_name = index_name or self.index_name

        try:
            await self.client.update(index=index_name, id=doc_id, doc=updates)
            logger.info(f"Document {doc_id} updated")
            return True
        except NotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise


# Singleton instance
es_service = ElasticsearchService()
