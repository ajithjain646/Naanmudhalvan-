"""
Concept Explanation Module for EduGenie - AI-Powered Learning Assistant.
Uses a lightweight local model (LaMini-Flan-T5 / Hugging Face pipeline)
with intelligent fallback to generate easy-to-understand explanations for beginners.

Structure:
- Simple Definition
- Step-by-Step Explanation
- Real-World Example
- Important Points
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("edugenie.explanation")

# Global cache for the local pipeline
_LOCAL_PIPELINE = None
_LOCAL_MODEL_ATTEMPTED = False

def get_local_model_pipeline():
    """
    Lazily loads the local HuggingFace pipeline (LaMini-Flan-T5).
    Cached globally to avoid reloading on each request.
    """
    global _LOCAL_PIPELINE, _LOCAL_MODEL_ATTEMPTED
    if _LOCAL_PIPELINE is not None:
        return _LOCAL_PIPELINE

    if _LOCAL_MODEL_ATTEMPTED:
        return None

    _LOCAL_MODEL_ATTEMPTED = True
    model_name = os.getenv("LOCAL_MODEL_NAME", "MBZUAI/LaMini-Flan-T5-248M")

    try:
        from transformers import pipeline
        logger.info(f"Loading local explanation model: {model_name}...")
        pipe = pipeline(
            "text2text-generation",
            model=model_name,
            max_length=512,
            do_sample=True,
            temperature=0.7
        )
        _LOCAL_PIPELINE = pipe
        logger.info(f"Successfully loaded local model {model_name}.")
        return _LOCAL_PIPELINE
    except Exception as e:
        logger.warning(
            f"Local model '{model_name}' could not be loaded ({e}). "
            "EduGenie will use high-performance cloud/algorithmic fallback for explanations."
        )
        return None

def _gemini_explain(topic: str) -> Optional[str]:
    """
    Fallback using Google Gemini when local model is unavailable or constrained.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = (
            f"You are EduGenie, an expert educator explaining a concept to a beginner.\n"
            f"Concept to explain: '{topic}'\n\n"
            f"Please structure your explanation clearly with the following sections:\n"
            f"### 1. Simple Definition\n"
            f"A one-paragraph, plain-English summary of what this is.\n\n"
            f"### 2. Step-by-Step Explanation\n"
            f"Break down how it works or how to understand it in clear, logical steps.\n\n"
            f"### 3. Clear Example\n"
            f"A concrete, relatable real-world or mathematical example illustrating the concept.\n\n"
            f"### 4. Important Points to Remember\n"
            f"3-4 key takeaways or common pitfalls for a student.\n\n"
            f"Keep the tone encouraging, crystal-clear, and engaging."
        )
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini explanation fallback failed: {e}")
    return None

def _pedagogical_template_explain(topic: str) -> str:
    """
    Structured educational template fallback for offline/isolated environments.
    """
    return (
        f"### 1. Simple Definition\n"
        f"**{topic}** is a fundamental concept in its domain. At its core, it provides a "
        f"systematic way to understand, analyze, or solve problems related to this topic "
        f"by breaking complex interactions into understandable components.\n\n"
        f"### 2. Step-by-Step Explanation\n"
        f"1. **Core Principle**: Grasp the foundational idea behind {topic} and the specific problem it addresses.\n"
        f"2. **Mechanics**: Observe how individual parts interact together under rules or conditions.\n"
        f"3. **Application**: Apply the principles to systematically achieve a predictable, verifiable outcome.\n\n"
        f"### 3. Clear Example\n"
        f"Consider applying **{topic}** in a practical scenario: when you encounter a problem involving this concept, "
        f"you identify the known variables, utilize standard formulas or principles, and arrive at the solution step by step.\n\n"
        f"### 4. Important Points to Remember\n"
        f"- Always verify foundational assumptions before applying complex rules.\n"
        f"- Practice with small, manageable examples first.\n"
        f"- Review common edge cases to build intuition and confidence."
    )

def explain_concept(topic: str) -> Dict[str, Any]:
    """
    Explains an educational concept suitable for beginners.

    Args:
        topic: The topic or concept name.

    Returns:
        Dict with "explanation", "topic", and "model_used".
    """
    clean_topic = topic.strip() if topic else ""
    if not clean_topic:
        raise ValueError("Topic cannot be empty.")

    # 1. Try local model pipeline (LaMini-Flan-T5)
    local_pipe = get_local_model_pipeline()
    if local_pipe is not None:
        try:
            instruction = (
                f"Explain the concept of '{clean_topic}' to a beginner student. "
                "Include a simple definition, step-by-step explanation, an example, and key points."
            )
            output = local_pipe(instruction, max_length=512, truncation=True)
            if output and len(output) > 0 and "generated_text" in output[0]:
                explanation_text = output[0]["generated_text"].strip()
                return {
                    "topic": clean_topic,
                    "explanation": explanation_text,
                    "model_used": "LaMini-Flan-T5 (Local Model)"
                }
        except Exception as e:
            logger.warning(f"Error during local model inference: {e}")

    # 2. Try Gemini educational explanation
    gemini_result = _gemini_explain(clean_topic)
    if gemini_result:
        return {
            "topic": clean_topic,
            "explanation": gemini_result,
            "model_used": "Google Gemini (Structured Educational Explainer)"
        }

    # 3. Deterministic pedagogical fallback
    fallback_text = _pedagogical_template_explain(clean_topic)
    return {
        "topic": clean_topic,
        "explanation": fallback_text,
        "model_used": "EduGenie Core Explainer"
    }
