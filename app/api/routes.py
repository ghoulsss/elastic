from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.document import Document
from app.schemas.search import SearchQuery, SearchResponse
from app.services.elasticsearch_service import es_service

router = APIRouter(prefix="/api/v1", tags=["search"])


async def get_es_service():
    """Dependency для получения ES сервиса"""
    return es_service


@router.post("/documents", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_document(
    document: Document,
    service: es_service = Depends(get_es_service),
):
    """Создание нового документа"""
    try:
        doc_id = await service.index_document(document)
        return {"id": doc_id, "message": "Document created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/bulk", status_code=status.HTTP_201_CREATED)
async def create_documents_bulk(
    documents: List[Document], service: es_service = Depends(get_es_service)
):
    """Массовое создание документов"""
    try:
        result = await service.bulk_index(documents)
        return {
            "indexed": len(documents),
            "errors": result.get("errors", False),
            "message": "Documents indexed successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    search_query: SearchQuery, service: es_service = Depends(get_es_service)
):
    """Поиск документов"""
    try:
        results = await service.search(search_query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str, service: es_service = Depends(get_es_service)):
    """Получение документа по ID"""
    document = await service.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/documents/{doc_id}")
async def update_document(
    doc_id: str, updates: dict, service: es_service = Depends(get_es_service)
):
    """Обновление документа"""
    success = await service.update_document(doc_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document updated successfully"}


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str, service: es_service = Depends(get_es_service)):
    """Удаление документа"""
    success = await service.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None
