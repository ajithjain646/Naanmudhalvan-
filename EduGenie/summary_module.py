"""
Summarization Module for EduGenie - AI-Powered Learning Assistant.
Summarizes long educational passages and articles into concise, high-yield
summaries suitable for quick revision while retaining all core concepts.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("edugenie.summary")

def summarize_text(passage: str) -> Dict[str, Any]:
    """
    Summarizes an educational text passage using Gemini.

    Args:
        passage: The long educational text or article.

    Returns:
        Dict with "summary" key containing the concise summary and key takeaways.
    """
    clean_text = passage.strip() if passage else ""
    if not clean_text:
        raise ValueError("Text passage cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file."
        )

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            "You are EduGenie, an expert educational content summarizer. "
            "Your goal is to simplify and condense the following passage for quick student revision, "
            "retaining all essential facts, core definitions, and key takeaways.\n\n"
            "Format the summary as:\n"
            "1. **Core Summary**: A concise 2-3 sentence overview.\n"
            "2. **Key Takeaways**: Bullet points highlighting critical points.\n\n"
            f"Passage to summarize:\n{clean_text}\n"
        )

        response = model.generate_content(prompt)
        if not response or not response.text:
            raise RuntimeError("Received empty response from Gemini.")

        return {"summary": response.text.strip()}

    except Exception as e:
        logger.error(f"Summarization error: {e}")
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            raise ValueError("The provided Gemini API key is invalid.")
        raise RuntimeError("Something went wrong while generating the summary. Please try again.")
