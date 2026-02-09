"""
PDF Controller

Handles PDF processing: read, chunk, embed, and store in Chroma Cloud.
"""

import os
from app.services.rag_pipeline import process_pdf


def process_pdf_from_path(pdf_path: str) -> dict:
    """
    Process a PDF file from a file path.

    Steps:
    1. Extract text from PDF
    2. Split into 500-char chunks
    3. Generate embeddings (768-dim vectors)
    4. Store in Chroma Cloud

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

    Raises:
        FileNotFoundError: If PDF doesn't exist
        Exception: If processing fails
    """

    """ os lets you interact with the Operating System """
    if not os.path.exists(pdf_path): 
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    result = process_pdf(pdf_path)

    if not result['success']:
        raise Exception(result['error'])

    return result


def process_uploaded_pdf(file_content: bytes, filename: str) -> dict:
    
    # Validate file type
    if not filename.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF (.pdf)")

    # Create temp directory
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)

    try:
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Process
        result = process_pdf(file_path)

        if not result['success']:
            raise Exception(result['error'])

        return {
            **result,
            "filename": filename
        }

    finally:
        # Clean up
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to delete temp file: {e}")
