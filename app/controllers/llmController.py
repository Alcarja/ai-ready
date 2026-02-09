"""
LLM Controller

Handles LLM operations including question vectorization and knowledge base search.
"""

import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv
import os
from app.chroma_connection import get_chroma_collection_direct

load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)  # type: ignore


def ask_llm(question: str) -> dict:
    """
    Vectorize the user question and search Chroma for the 5 most similar documents.

    Args:
        question: The question to vectorize and search

    Returns:
        {
            'question': str (original question),
            'embedding': list[float] (vector representation of the question),
            'embedding_model': str (model used),
            'status': 'success' or 'error',
            'search_results': [
                {
                    'document': str,
                    'similarity': float (0-1),
                    'chunk_id': str,
                    'metadata': dict
                },
                ...
            ]
        }
    """
    try:
        # Step 1: Vectorize the question using Google's embedding API
        response = genai.embed_content(  # type: ignore
            model="models/gemini-embedding-001",
            content=question
        )
        question_embedding = response['embedding']

        # Step 2: Search Chroma for 5 most similar documents
        collection = get_chroma_collection_direct()
        search_results = collection.query(
            query_embeddings=[question_embedding],
            n_results=5
        )

        # Step 3: Format search results
        formatted_results = []
        docs_list = search_results.get('documents') if search_results else None
        dist_list = search_results.get('distances') if search_results else None
        meta_list = search_results.get('metadatas') if search_results else None

        if docs_list and isinstance(docs_list, list) and len(docs_list) > 0:
            documents = docs_list[0] if docs_list else []
            distances = dist_list[0] if (dist_list and isinstance(dist_list, list) and len(dist_list) > 0) else []
            metadatas = meta_list[0] if (meta_list and isinstance(meta_list, list) and len(meta_list) > 0) else []

            for i, doc in enumerate(documents):
                distance = distances[i] if i < len(distances) else 0
                similarity_score = round(1 - distance, 2)  # Convert distance to similarity (0-1)
                metadata = metadatas[i] if i < len(metadatas) else {}

                formatted_results.append({
                    "document": doc,
                    "similarity": similarity_score,
                    "chunk_id": metadata.get('chunk_id', 'unknown') if isinstance(metadata, dict) else 'unknown',
                    "metadata": metadata
                })

        return {
            "question": question,
            "embedding": question_embedding,
            "embedding_model": "gemini-embedding-001",
            "status": "success",
            "search_results": formatted_results
        }

    except Exception as e:
        return {
            "question": question,
            "embedding": None,
            "embedding_model": "gemini-embedding-001",
            "status": "error",
            "error": str(e),
            "search_results": []
        }
