"""
API routes for managing documents in Chroma.
Includes endpoints for adding, querying, and managing documents.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from chromadb.api.models.Collection import Collection
from app.chroma_connection import get_chroma_collection


class AddDocumentsRequest(BaseModel):
    """Request body for adding documents to Chroma"""
    ids: list[str]
    documents: list[str]
    metadatas: list[dict] | None = None
    embeddings: list[list[float]] | None = None


class QueryRequest(BaseModel):
    """Request body for querying documents"""
    query_texts: list[str] | None = None
    query_embeddings: list[list[float]] | None = None
    n_results: int = 5
    where: dict | None = None


class QueryResponse(BaseModel):
    """Response for document queries"""
    ids: list[list[str]]
    documents: list[list[str]]
    distances: list[list[float]]
    metadatas: list[list[dict]]


router = APIRouter(prefix="/documents", tags=["chroma"])


@router.post("/add/")
async def add_documents(
    request: AddDocumentsRequest,
    collection: Collection = Depends(get_chroma_collection)
):
    """
    Add documents to the Chroma collection.

    Args:
        request: Contains ids, documents, and optional metadatas/embeddings
        collection: Chroma collection (injected via Depends)

    Returns:
        Success message with document IDs
    """
    try:
        # Ensure metadatas is provided (required by Chroma)
        metadatas = request.metadatas if request.metadatas else [{} for _ in request.ids]

        collection.add(
            ids=request.ids,
            documents=request.documents,
            metadatas=metadatas,
            embeddings=request.embeddings if request.embeddings else None
        )
        return {
            "message": "Documents added successfully",
            "count": len(request.ids),
            "ids": request.ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")


@router.post("/query/")
async def query_documents(
    request: QueryRequest,
    collection: Collection = Depends(get_chroma_collection)
):
    """
    Query documents from the Chroma collection.

    Args:
        request: Contains query_texts or query_embeddings
        collection: Chroma collection (injected via Depends)

    Returns:
        Query results with documents and distances
    """
    try:
        results = collection.query(
            query_texts=request.query_texts,
            query_embeddings=request.query_embeddings,
            n_results=request.n_results,
            where=request.where
        )
        return {
            "ids": results.get("ids", []),
            "documents": results.get("documents", []),
            "distances": results.get("distances", []),
            "metadatas": results.get("metadatas", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")


@router.get("/count/")
async def get_document_count(collection: Collection = Depends(get_chroma_collection)):
    """
    Get the total count of documents in the collection.

    Returns:
        Document count
    """
    try:
        count = collection.count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting count: {str(e)}")


@router.delete("/{document_id}/")
async def delete_document(
    document_id: str,
    collection: Collection = Depends(get_chroma_collection)
):
    """
    Delete a document from the collection.

    Args:
        document_id: ID of the document to delete
        collection: Chroma collection (injected via Depends)

    Returns:
        Success message
    """
    try:
        collection.delete(ids=[document_id])
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
