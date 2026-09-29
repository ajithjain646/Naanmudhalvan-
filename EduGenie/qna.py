"""
Q&A Module for EduGenie - AI-Powered Learning Assistant.
Handles student questions using Google Gemini API to produce concise,
accurate, and student-friendly answers.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("edugenie.qna")

def get_gemini_client():
    """
    Initializes and returns a configured Google Gemini generative model instance.
    Raises ValueError if GEMINI_API_KEY is not configured.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file."
        )

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash for fast, accurate educational responses
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        raise RuntimeError(f"Error initializing Gemini AI service: {str(e)}")

def answer_question(question_text: str) -> Dict[str, Any]:
    """
    Answers a student's question using Gemini.

    Args:
        question_text: The question asked by the student.

    Returns:
        Dict with "answer" key containing the concise, accurate response.
    """
    clean_text = question_text.strip() if question_text else ""
    if not clean_text:
        raise ValueError("Question text cannot be empty.")

    model = get_gemini_client()

    prompt = (
        "You are EduGenie, an empathetic, highly knowledgeable AI educational tutor. "
        "Answer the following student question concisely, accurately, and in an encouraging, "
        "easy-to-understand manner suitable for students and self-learners.\n\n"
        f"Question: {clean_text}\n\n"
        "Provide a clear, student-friendly answer directly without unnecessary preamble."
    )

    try:
        response = model.generate_content(prompt)
        if not response or not response.text:
            raise RuntimeError("Received empty response from Gemini AI.")
        
        answer = response.text.strip()
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Gemini API error during Q&A generation: {e}")
        # Safeguard sensitive credentials and return friendly message
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid api key" in error_msg.lower():
            raise ValueError("The provided Gemini API key is invalid. Please verify your GEMINI_API_KEY.")
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            raise RuntimeError("AI service quota reached or rate-limited. Please try again shortly.")
        else:
            raise RuntimeError("Something went wrong while generating your response. Please try again.")
