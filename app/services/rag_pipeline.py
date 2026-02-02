from app.services.pdf_reader import read_pdf
from app.services.text_chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import store_embeddings


def process_pdf(pdf_path: str, store_dir: str = "data/vector_store") -> dict:
    """
    Complete RAG pipeline: read PDF, chunk, embed, and store in vector DB.

    Args:
        pdf_path: Path to the PDF file to process
        store_dir: Directory to save FAISS index and metadata

    Returns:
        Dictionary with processing results:
        {
            'success': bool,
            'pdf_path': str,
            'chunks_count': int,
            'vectors_stored': int,
            'index_path': str,
            'metadata_path': str,
            'error': str (if failed)
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
        print("Generating embeddings...")
        try:
            chunks_with_embeddings = generate_embeddings(chunks)
            print(f"Embeddings generated for {len(chunks_with_embeddings)} chunks")
        except Exception as embed_error:
            raise Exception(f"Embedding generation failed: {str(embed_error)}")

        # Step 4: Store in Chroma
        print("Storing in vector database...")
        try:
            storage_result = store_embeddings(chunks_with_embeddings, store_dir)
            print(f"Vector database saved to {storage_result['db_path']}")
        except Exception as store_error:
            raise Exception(f"Vector storage failed: {str(store_error)}")

        return {
            'success': True,
            'pdf_path': pdf_path,
            'chunks_count': len(chunks),
            'vectors_stored': storage_result['vector_count'],
            'db_path': storage_result['db_path'],
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
            'index_path': None,
            'metadata_path': None,
            'error': error_msg
        }
