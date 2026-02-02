"""
Manual RAG setup script.
Run this file to process PDFs and populate the vector database.

Usage:
    python setup_rag.py
"""

from app.services.rag_pipeline import process_pdf


def main():
    # Add your PDF file paths here
    pdf_files = [
        # Example:
        # "path/to/document1.pdf",
        # "path/to/document2.pdf",
        #"./PDFs/politica_gastos.pdf",
        "./PDFs/politica_vacaciones.pdf"
    ]

    if not pdf_files:
        print("❌ No PDF files specified!")
        print("Add PDF file paths to the 'pdf_files' list in this script.")
        return

    print("=" * 60)
    print("RAG Setup - Processing PDFs")
    print("=" * 60)

    successful = 0
    failed = 0

    for pdf_path in pdf_files:
        print(f"\n📄 Processing: {pdf_path}")
        print("-" * 60)

        result = process_pdf(pdf_path)

        if result['success']:
            successful += 1
            print(f"✅ Success!")
            print(f"   Chunks created: {result['chunks_count']}")
            print(f"   Vectors stored: {result['vectors_stored']}")
            print(f"   Database path: {result['db_path']}")
            print(f"   Collection: {result['collection_name']}")
        else:
            failed += 1
            print(f"❌ Failed: {result['error']}")

    print("\n" + "=" * 60)
    print(f"Summary: {successful} succeeded, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
