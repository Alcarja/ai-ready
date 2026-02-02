def chunk_text (text: str, chunk_size: int, overlap: int = 50) -> list[dict]:
    """Split text into overlapping chunks of fixed size"""

#    Returns: [
#   {'chunk_id': 0, 'text': '--- Page 1 ---\nSome text...', 'start_pos': 0, 'end_pos': 500},
#   {'chunk_id': 1, 'text': 'Some text...\nMore text...', 'start_pos': 450, 'end_pos': 950},
#   ]

    chunks = []
    chunk_id = 0
    start_pos = 0

    while start_pos < len(text):
        # Calculate end position
        end_pos = min(start_pos + chunk_size, len(text))

        # Extract chunk
        chunk_text = text[start_pos:end_pos]

        # Create chunk object
        chunks.append({
            'chunk_id': chunk_id,
            'text': chunk_text,
            'start_pos': start_pos,
            'end_pos': end_pos
        })

        chunk_id += 1

        # Move start position, accounting for overlap
        start_pos = end_pos - overlap

        # Prevent infinite loop if we reach the end
        if end_pos == len(text):
            break

    return chunks