import chromadb
import os


def store_embeddings(chunks_with_embeddings: list[dict], store_dir: str = "data/vector_store") -> dict:
    """
    Store embeddings in Chroma vector database.

    Args:
        chunks_with_embeddings: List of chunks from generate_embeddings()
                               Each chunk has: chunk_id, text, embedding, etc.
        store_dir: Directory to persist Chroma database

    Returns:
        Dictionary with database info:
        {
            'db_path': str,
            'collection_name': str,
            'vector_count': int
        }

    Raises:
        Exception: If there's an error storing embeddings
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(store_dir, exist_ok=True)

        # Initialize Chroma client
        client = chromadb.PersistentClient(path=store_dir)
        collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        # Add embeddings and metadata to Chroma
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks_with_embeddings:
            chunk_id = f"chunk_{chunk['chunk_id']}"
            ids.append(chunk_id)
            embeddings.append(chunk['embedding'])
            documents.append(chunk['text'])
            metadatas.append({
                'chunk_id': str(chunk['chunk_id']),
                'start_pos': str(chunk.get('start_pos', '')),
                'end_pos': str(chunk.get('end_pos', ''))
            })

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return {
            'db_path': store_dir,
            'collection_name': 'documents',
            'vector_count': len(chunks_with_embeddings)
        }

    except Exception as e:
        raise Exception(f"Error storing embeddings in Chroma: {str(e)}")


def get_collection(store_dir: str = "data/vector_store"):
    """
    Get Chroma collection for querying.

    Args:
        store_dir: Directory containing Chroma database

    Returns:
        Chroma collection object

    Raises:
        Exception: If collection can't be loaded
    """
    try:
        client = chromadb.PersistentClient(path=store_dir)
        collection = client.get_collection(name="documents")
        return collection

    except Exception as e:
        raise Exception(f"Error loading Chroma collection: {str(e)}")


def search_similar_chunks(query_embedding: list, store_dir: str = "data/vector_store", top_k: int = 5) -> list[dict]:
    """
    Search for similar chunks given a query embedding.

    Args:
        query_embedding: Embedding vector of the query (from generate_embeddings)
        store_dir: Directory containing Chroma database
        top_k: Number of top results to return (default: 5)

    Returns:
        List of similar chunks with their metadata:
        [
            {
                'chunk_id': int,
                'text': str,
                'distance': float,
                'start_pos': int,
                'end_pos': int
            },
            ...
        ]
    """
    try:
        collection = get_collection(store_dir)

        # Search Chroma (returns results sorted by distance)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results and results['documents'] and len(results['documents']) > 0:
            # Helper to safely convert metadata values to int
            def safe_int(value) -> int | None:  # type: ignore
                if value is None:
                    return None
                try:
                    str_value = str(value).strip()
                    return int(str_value) if str_value else None
                except (ValueError, TypeError, AttributeError):
                    return None

            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}

                formatted_results.append({
                    'chunk_id': safe_int(metadata.get('chunk_id')) or 0,
                    'text': doc,
                    'distance': float(results['distances'][0][i]),
                    'start_pos': safe_int(metadata.get('start_pos')),
                    'end_pos': safe_int(metadata.get('end_pos'))
                })

        return formatted_results

    except Exception as e:
        raise Exception(f"Error searching Chroma: {str(e)}")
