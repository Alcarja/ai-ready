"""
PDF Processing Routes

Process PDFs: chunk, generate embeddings, and store in Chroma Cloud.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from app.controllers.pdfController import (
    process_pdf_from_path,
    process_uploaded_pdf,
)


class ProcessPDFRequest(BaseModel):
    """Request to process a PDF from file path"""
    pdf_path: str


class ProcessPDFResponse(BaseModel):
    """Response from PDF processing"""
    success: bool
    pdf_path: str
    chunks_count: int
    vectors_stored: int
    collection_name: str
    error: str | None


router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/process/", response_model=ProcessPDFResponse)
def process_pdf_endpoint(request: ProcessPDFRequest):
    """
    Process a PDF file and store in Chroma Cloud.

    Args:
        pdf_path: Path to the PDF file (e.g., "documents/manual.pdf")

    Returns:
        Processing result with chunks and vectors stored
    """
    try:
        result = process_pdf_from_path(request.pdf_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/upload/")
async def upload_and_process(file: UploadFile = File(...)):
    """
    Upload a PDF and process it directly.

    Args:
        file: PDF file to upload

    Returns:
        Processing result with filename
    """
    try:
        content = await file.read()
        result = process_uploaded_pdf(content, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
