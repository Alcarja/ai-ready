"""
Tool for searching the knowledge base using vector similarity.

Queries Chroma Cloud with a pre-computed embedding of the search query.
Uses Google's gemini-embedding-001 model to embed the query.
"""

import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv
import os
from app.chroma_connection import get_chroma_collection_direct

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)  # type: ignore


def search_knowledge_base(query: str, top_k: int = 3) -> dict:
    """
    Search the knowledge base for information similar to the query.

    Generates an embedding for the query using embedding-gecko-002
    and searches for similar documents in Chroma.

    Args:
        query: The user's question or search query
        top_k: Number of top results to return (default: 3)

    Returns:
        {
            'status': 'success' or 'error',
            'results': Text of similar documents,
            'message': Description or error message
        }
    """
    try:
        # Step 1: Generate embedding for the query
        query_embedding_response = genai.embed_content(  # type: ignore
            model="models/gemini-embedding-001",
            content=query
        )
        query_embedding = query_embedding_response['embedding']

        # Step 2: Query Chroma with the embedding vector
        collection = get_chroma_collection_direct()
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results for the agent
        if search_results and search_results.get('documents') and len(search_results['documents']) > 0:
            documents = search_results['documents'][0]
            distances = search_results['distances'][0] if search_results.get('distances') else []

            # Create formatted results with similarity scores
            results_list = []
            for i, doc in enumerate(documents):
                distance = distances[i] if i < len(distances) else 0
                similarity_score = round(1 - distance, 2)  # Convert distance to similarity (0-1)
                doc_preview = doc[:200] + "..." if len(doc) > 200 else doc
                results_list.append(f"- [{similarity_score}] {doc_preview}")

            results_text = "\n".join(results_list)
            return {
                "status": "success",
                "results": results_text,
                "message": f"Found {len(documents)} relevant documents"
            }
        else:
            return {
                "status": "success",
                "results": "No relevant documents found",
                "message": "The knowledge base does not contain information matching your query"
            }

    except Exception as e:
        return {
            "status": "error",
            "results": "",
            "message": f"Error searching knowledge base: {str(e)}"
        }
