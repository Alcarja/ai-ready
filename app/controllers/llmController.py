import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv
import os

load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)  # type: ignore


def ask_llm(question: str, system_prompt: str | None = None) -> str:
    """Send a question to Google's Gemini LLM and get a response"""
    # Default system prompt for HR assistant
    if system_prompt is None:
        system_prompt = """You are an HR (Human Resources) assistant.
Your role is to help with HR-related questions including:
- Employee policies
- Benefits and compensation
- Payroll
- Recruitment
- Performance management
- Training and development

If a question is not related to HR, politely decline and redirect the user back to HR topics."""

    model = genai.GenerativeModel(  # type: ignore
        "gemini-2.0-flash",
        system_instruction=system_prompt
    )
    response = model.generate_content(question)
    return response.text
