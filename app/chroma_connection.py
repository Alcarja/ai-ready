"""
Chroma Cloud connection management with FastAPI Depends integration.
Provides singleton instances of Chroma client and collection.
"""

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from fastapi import Depends
from dotenv import load_dotenv
import os

load_dotenv()

_client: ClientAPI | None = None
_collection: Collection | None = None


def get_chroma_client() -> ClientAPI:
    """
    Get or create a Chroma Cloud client.
    Uses environment variables for authentication.

    Environment variables required:
    - CHROMA_API_KEY: Your Chroma API key
    - CHROMA_TENANT: Your Chroma tenant name
    - CHROMA_DATABASE: Your Chroma database name

    Returns:
        ClientAPI: Chroma Cloud client instance (singleton)
    """
    global _client
    if _client is None:
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT")
        database = os.getenv("CHROMA_DATABASE")

        if not all([api_key, tenant, database]):
            raise ValueError(
                "Missing Chroma Cloud credentials. "
                "Please set CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE in .env"
            )

        _client = chromadb.CloudClient(
            api_key=api_key,
            tenant=tenant,
            database=database
        )
    return _client


def get_chroma_collection_direct() -> Collection:
    """
    Direct utility function to get or create the default Chroma collection.
    Use this from service layer code (rag_pipeline, search_knowledge_base, etc).

    Uses embedding_function=None because embeddings are pre-computed with Google's API.

    Returns:
        Collection: Chroma collection instance (singleton)
    """
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
            embedding_function=None  # Pre-computed embeddings only
        )
    return _collection


def get_chroma_collection(client: ClientAPI = Depends(get_chroma_client)) -> Collection:
    """
    FastAPI dependency function to get or create the default Chroma collection.
    Use this in route handlers with Depends injection.

    Args:
        client: Chroma client (injected via Depends)

    Returns:
        Collection: Chroma collection instance (singleton)
    """
    return get_chroma_collection_direct()


def close_chroma_connection():
    """
    Close the Chroma connection.
    Call this in FastAPI shutdown event if needed.
    """
    global _client, _collection
    _client = None
    _collection = None
