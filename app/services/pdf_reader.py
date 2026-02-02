import pdfplumber


def read_pdf(file_path: str) -> str:
    """
    Read a PDF file and extract all text from it.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text from all pages concatenated with page separators

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error reading the PDF
    """
    try:
        full_text = ""

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    full_text += f"--- Page {page_num} ---\n{text}\n"

        return full_text

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

