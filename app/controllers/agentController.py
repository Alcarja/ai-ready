"""
Agent Controller

Uses Google Gemini with tool use to create an intelligent agent
that can decide when to check the knowledge base.
"""

import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv
import os
import json
from agent.tools.check_db import check_db

load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)  # type: ignore


# Define the check_db tool for the agent
CHECK_DB_TOOL = {
    "name": "check_db",
    "description": "Search the knowledge base (Chroma DB) for documents similar to the user's question. Use this when you need to find relevant information from stored documents.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "question": {
                "type": "STRING",
                "description": "The question to search for in the knowledge base"
            }
        },
        "required": ["question"]
    }
}


def ask_agent(user_question: str) -> dict:
    """
    Use an agent with tool use to answer user questions.

    The agent can decide whether to use the check_db tool
    to search the knowledge base or answer from general knowledge.

    Args:
        user_question: The user's question

    Returns:
        {
            'status': 'success' or 'error',
            'answer': str (formatted response from agent),
            'tool_used': bool (whether check_db was called),
            'error': str or None
        }
    """
    try:
        # System prompt for the agent
        system_prompt = """You are a helpful HR assistant with access to a knowledge base.

You have access to a tool called 'check_db' that lets you search a knowledge base for relevant documents.

Instructions:
1. When a user asks a question, decide if you need to check the knowledge base
2. Use check_db when:
   - The question is about HR policies, procedures, or specific information
   - You might find relevant documents in the knowledge base
3. Don't use check_db when:
   - The question is a simple greeting or general conversation
   - You're confident you can answer from general knowledge
4. After getting results (or deciding not to use the tool), provide a clear, helpful answer
5. If you use check_db, mention that the information comes from the knowledge base
6. Always format your response clearly and professionally"""

        # Create the model with tool use capability and system instruction
        model = genai.GenerativeModel(  # type: ignore
            "gemini-2.0-flash",
            tools=[CHECK_DB_TOOL],
            system_instruction=system_prompt
        )

        # Create conversation with user question using proper format
        messages = [user_question]  # Just pass the text directly

        # First API call - let agent decide if it needs to use the tool
        response = model.generate_content(messages[0])

        tool_used = False
        final_answer = ""

        # Check if the agent wants to use a tool
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]

            # Process tool calls if any
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        # Agent wants to use the check_db tool
                        tool_used = True
                        tool_call = part.function_call

                        if tool_call.name == "check_db":
                            # Get the question from tool input
                            db_question = user_question  # Default fallback
                            try:
                                # Convert args to dict
                                args_dict = {}
                                if hasattr(tool_call.args, '__dict__'):
                                    args_dict = vars(tool_call.args)
                                elif isinstance(tool_call.args, dict):
                                    args_dict = tool_call.args
                                else:
                                    args_dict = json.loads(str(tool_call.args))

                                db_question = args_dict.get("question", user_question)
                            except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
                                # Fallback to original question
                                pass

                            # Call the check_db tool
                            db_results = check_db(db_question)

                            # Build message content for continuation
                            # Google's API expects a list of either strings or Content objects with the conversation history
                            continuation_text = f"Here are the results from the knowledge base:\n\n{db_results}\n\nNow please answer the original question based on this information."

                            # Create a list with the original question and the tool result
                            messages_list = [
                                user_question,
                                continuation_text
                            ]

                            # Get final response from agent by passing the full context
                            final_response = model.generate_content(messages_list)

                            if hasattr(final_response, 'text') and final_response.text:
                                final_answer = final_response.text
                            else:
                                final_answer = "Could not generate a response."

                    elif hasattr(part, 'text') and part.text:
                        # Agent provided text without using tools
                        final_answer = part.text

        # If no tool was used but agent responded
        if not tool_used and not final_answer:
            final_answer = response.text if hasattr(response, 'text') else "No response generated"

        return {
            "status": "success",
            "answer": final_answer,
            "tool_used": tool_used,
            "error": None
        }

    except Exception as e:
        import traceback
        error_msg = f"Error in agent: {str(e)}"
        traceback.print_exc()  # Print full traceback for debugging
        return {
            "status": "error",
            "answer": "",
            "tool_used": False,
            "error": error_msg
        }
