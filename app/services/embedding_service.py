import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv
import os
import time

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)  # type: ignore


def generate_embeddings(chunks: list[dict]) -> list[dict]:
    """
    Generate embeddings for text chunks using Google's Embedding API.

    Args:
        chunks: List of chunk dictionaries from text_chunker
                Expected format: {'chunk_id': int, 'text': str, ...}

    Returns:
        List of chunk dictionaries with added 'embedding' field
        Each embedding is a list of floats (vector)

    Raises:
        Exception: If there's an error calling the embedding API
    """
    try:
        for chunk in chunks:
            # Call Google's embedding API
            response = genai.embed_content(  # type: ignore
                model="models/embedding-001",
                content=chunk['text']
            )

            # Add embedding to chunk
            chunk['embedding'] = response['embedding']

            # Delay to avoid rate limiting and API timeouts
            time.sleep(1)

        return chunks

    except Exception as e:
        raise Exception(f"Error generating embeddings: {str(e)}")
