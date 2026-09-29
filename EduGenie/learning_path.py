"""
Personalized Learning Path Module for EduGenie - AI-Powered Learning Assistant.
Generates structured beginner-to-advanced learning plans with timelines,
objectives, practice projects, and curated educational resources.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("edugenie.learning_path")

def _clean_json_string(raw_text: str) -> str:
    """Strips markdown code fences to isolate JSON payload."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1].strip()
    return text

def _generate_fallback_learning_path(topic: str) -> Dict[str, Any]:
    """Provides a comprehensive structured roadmap when API key is unavailable."""
    return {
        "topic": topic,
        "timeline": "6 to 8 Weeks (5-7 hours per week)",
        "learning_objectives": [
            f"Master core terminology and fundamental mental models of {topic}",
            f"Build practical competence through hands-on intermediate exercises in {topic}",
            f"Analyze trade-offs, optimize performance, and understand advanced concepts"
        ],
        "learning_path": {
            "beginner": [
                {"title": "Foundations & Environment Setup", "description": f"Core terminology, prerequisites, and developer tools for {topic}."},
                {"title": "Basic Concepts & Syntax", "description": f"Essential rules, standard conventions, and syntax fundamentals."},
                {"title": "Core Operations & Workflows", "description": "Executing basic operations and inspecting immediate results."},
                {"title": "Simple Guided Exercises", "description": "Hands-on starter tasks reinforcing core understanding."}
            ],
            "intermediate": [
                {"title": "Modular Architecture & Relationships", "description": f"How different components in {topic} communicate and integrate."},
                {"title": "Data Flow & Transformation", "description": "Handling complex operations, aggregations, and edge cases."},
                {"title": "Debugging & Error Handling", "description": "Techniques for troubleshooting and avoiding common pitfalls."},
                {"title": "Intermediate Capstone Project", "description": "Building a working project consolidating intermediate techniques."}
            ],
            "advanced": [
                {"title": "Performance Optimization & Profiling", "description": "Benchmarking, caching, and tuning execution efficiency."},
                {"title": "Architectural Patterns & Best Practices", "description": "Industry design patterns, maintainability, and scalability."},
                {"title": "Security & Concurrency", "description": "Addressing security concerns, transactions, and state management."},
                {"title": "Production Deployment & Monitoring", "description": "Deploying, monitoring, and maintaining systems at scale."}
            ]
        },
        "practice_suggestions": [
            f"Build a mini project applying {topic} to solve a real-world problem",
            "Contribute to or review open-source repositories using this technology",
            "Write a technical blog post or notes teaching the concept to a peer"
        ],
        "recommended_resources": [
            {"name": f"Official {topic} Documentation", "type": "Documentation", "url": "https://devdocs.io"},
            {"name": "FreeCodeCamp & YouTube Crash Courses", "type": "Video Series", "url": "https://www.freecodecamp.org"},
            {"name": "Interactive Tutorials & Kata Challenges", "type": "Hands-on Practice", "url": "https://exercism.org"}
        ]
    }

def generate_learning_path(topic: str) -> Dict[str, Any]:
    """
    Generates a personalized, structured learning roadmap from beginner to advanced.

    Args:
        topic: The subject or technology to learn (e.g. 'SQL', 'Machine Learning').

    Returns:
        Structured dictionary containing roadmap stages, timeline, objectives,
        practice suggestions, and recommended resources.
    """
    clean_topic = topic.strip() if topic else ""
    if not clean_topic:
        raise ValueError("Topic cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        return _generate_fallback_learning_path(clean_topic)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = (
            "You are EduGenie, an expert curriculum designer and AI learning mentor. "
            f"Create a comprehensive, structured learning path for the topic: '{clean_topic}'.\n\n"
            "Organize the plan strictly from Beginner to Intermediate to Advanced.\n"
            "You MUST respond ONLY with valid JSON matching the following schema with NO surrounding markdown commentary:\n\n"
            "{\n"
            f'  "topic": "{clean_topic}",\n'
            '  "timeline": "Estimated completion timeline (e.g. 4-6 Weeks, 6 hrs/week)",\n'
            '  "learning_objectives": [\n'
            '    "Objective 1",\n'
            '    "Objective 2",\n'
            '    "Objective 3"\n'
            '  ],\n'
            '  "learning_path": {\n'
            '    "beginner": [\n'
            '      {"title": "Concept name", "description": "Brief explanation"}\n'
            '    ],\n'
            '    "intermediate": [\n'
            '      {"title": "Concept name", "description": "Brief explanation"}\n'
            '    ],\n'
            '    "advanced": [\n'
            '      {"title": "Concept name", "description": "Brief explanation"}\n'
            '    ]\n'
            '  },\n'
            '  "practice_suggestions": [\n'
            '    "Practical project or exercise 1",\n'
            '    "Practical project or exercise 2",\n'
            '    "Practical project or exercise 3"\n'
            '  ],\n'
            '  "recommended_resources": [\n'
            '    {"name": "Resource Name", "type": "Book / Video / Website", "url": "https://..."}\n'
            '  ]\n'
            "}"
        )

        response = model.generate_content(prompt)
        if not response or not response.text:
            return _generate_fallback_learning_path(clean_topic)

        clean_json = _clean_json_string(response.text)
        parsed = json.loads(clean_json)

        # Validate core keys exist
        if "learning_path" not in parsed or "beginner" not in parsed["learning_path"]:
            return _generate_fallback_learning_path(clean_topic)

        return parsed

    except Exception as e:
        logger.warning(f"Gemini learning path generation failed ({e}), using structured curriculum: {e}")
        return _generate_fallback_learning_path(clean_topic)
