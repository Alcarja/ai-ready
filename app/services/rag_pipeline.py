"""
RAG Pipeline - Process PDFs and store in Chroma Cloud

Flow:
1. Read PDF
2. Chunk text (500 chars)
3. Generate embeddings using Google's gemini-embedding-001
4. Store chunks + embeddings in Chroma Cloud
"""

from app.services.pdf_reader import read_pdf
from app.services.text_chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.chroma_connection import get_chroma_collection_direct


def store_chunks_in_chroma(chunks: list[dict]) -> dict:
    """
    Store chunks with pre-computed embeddings in Chroma Cloud.

    Args:
        chunks: List of chunks from text_chunker with 'embedding' field

    Returns:
        Storage result with vector count
    """
    try:
        collection = get_chroma_collection_direct()

        # Prepare data for Chroma
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in chunks:
            chunk_id = f"chunk_{chunk['chunk_id']}"
            ids.append(chunk_id)
            documents.append(chunk['text'])
            embeddings.append(chunk['embedding'])  # Pre-computed embedding
            metadatas.append({
                'chunk_id': str(chunk['chunk_id']),
                'start_pos': str(chunk.get('start_pos', '')),
                'end_pos': str(chunk.get('end_pos', ''))
            })

        # Add to Chroma with pre-computed embeddings
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,  # Pre-computed vectors
            metadatas=metadatas
        )

        return {
            'success': True,
            'vector_count': len(chunks),
            'collection_name': 'documents',
            'error': None
        }

    except Exception as e:
        error_msg = f"Error storing chunks in Chroma: {str(e)}"
        return {
            'success': False,
            'vector_count': 0,
            'collection_name': 'documents',
            'error': error_msg
        }


def process_pdf(pdf_path: str) -> dict:
    """
    Complete RAG pipeline: read PDF, chunk, generate embeddings, and store in Chroma Cloud.

    Steps:
    1. Extract text from PDF
    2. Split into 500-char chunks
    3. Generate embeddings using Google's gemini-embedding-001
    4. Store chunks + embeddings in Chroma Cloud

    Args:
        pdf_path: Path to the PDF file

    Returns:
        {
            'success': bool,
            'pdf_path': str,
            'chunks_count': int,
            'vectors_stored': int,
            'collection_name': str,
            'error': str or None
        }
    """
    try:
        # Step 1: Read PDF
        print(f"Reading PDF: {pdf_path}")
        pdf_text = read_pdf(pdf_path)
        print(f"PDF text extracted: {len(pdf_text)} characters")

        # Step 2: Chunk text
        print("Chunking text...")
        try:
            chunks = chunk_text(pdf_text, 500)
            print(f"Created {len(chunks)} chunks")
        except Exception as chunk_error:
            raise Exception(f"Chunking failed: {str(chunk_error)}")

        # Step 3: Generate embeddings
        print("Generating embeddings with gemini-embedding-001...")
        try:
            chunks_with_embeddings = generate_embeddings(chunks)
            print(f"Generated {len(chunks_with_embeddings)} embeddings")
        except Exception as embedding_error:
            raise Exception(f"Embedding generation failed: {str(embedding_error)}")

        # Step 4: Store in Chroma Cloud
        print("Storing chunks and embeddings in Chroma Cloud...")
        try:
            storage_result = store_chunks_in_chroma(chunks_with_embeddings)

            if not storage_result.get('success', False):
                raise Exception(storage_result.get('error', 'Unknown storage error'))

            print(f"Stored {storage_result['vector_count']} chunks with embeddings in Chroma Cloud")
        except Exception as store_error:
            raise Exception(f"Storage failed: {str(store_error)}")

        return {
            'success': True,
            'pdf_path': pdf_path,
            'chunks_count': len(chunks_with_embeddings),
            'vectors_stored': storage_result['vector_count'],
            'collection_name': storage_result['collection_name'],
            'error': None
        }

    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'pdf_path': pdf_path,
            'chunks_count': 0,
            'vectors_stored': 0,
            'collection_name': 'documents',
            'error': error_msg
        }
