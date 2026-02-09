"""
Tool for the agent to check the knowledge base (Chroma DB).

The agent can use this tool to search for relevant documents
when handling user questions.
"""

from app.controllers.llmController import ask_llm


def check_db(question: str) -> str:
    """
    Check the knowledge base for information related to the user's question.

    This tool:
    1. Vectorizes the question
    2. Searches Chroma for 5 most similar documents
    3. Returns formatted results

    Args:
        question: The user's question to search for

    Returns:
        Formatted string with search results and similarity scores
    """
    try:
        result = ask_llm(question)

        if result['status'] == 'error':
            return f"Error searching knowledge base: {result.get('error', 'Unknown error')}"

        search_results = result.get('search_results', [])

        if not search_results:
            return "No relevant documents found in the knowledge base."

        # Format results as a readable string for the agent
        formatted_results = "Found the following relevant documents:\n\n"

        for i, doc_result in enumerate(search_results, 1):
            similarity = doc_result.get('similarity', 0)
            document = doc_result.get('document', '')
            chunk_id = doc_result.get('chunk_id', 'unknown')

            # Truncate long documents for readability
            doc_preview = document[:300] + "..." if len(document) > 300 else document

            formatted_results += f"{i}. [Similarity: {similarity}] (Chunk: {chunk_id})\n"
            formatted_results += f"   {doc_preview}\n\n"

        return formatted_results

    except Exception as e:
        return f"Error accessing knowledge base: {str(e)}"
