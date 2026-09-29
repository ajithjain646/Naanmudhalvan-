"""
Comprehensive Unit and Integration Tests for EduGenie
Tests all REST endpoints: /, /health, /qa, /explain, /quiz, /summarize, /learn/recommendations.
Validates:
- Valid inputs and successful responses
- Empty input validation (400)
- Missing/invalid schema validation (422)
- Resilient error handling upon AI/API failure (500)
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from main import app


@pytest.fixture
def client():
    """Returns a FastAPI TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


# =====================================================================
# 1. Root & Health Check Tests
# =====================================================================

def test_read_root_dashboard(client):
    """Verifies that GET / renders the Jinja2 HTML dashboard template."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "EduGenie" in response.text
    assert "Your AI-Powered Learning Assistant" in response.text
    assert "task-select" in response.text


def test_health_check(client):
    """Verifies that GET /health returns application status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert data.get("app") == "EduGenie"
    assert "gemini_configured" in data


# =====================================================================
# 2. Feature 1: /qa Tests
# =====================================================================

def test_qa_valid_input_mocked(client):
    """Verifies POST /qa with valid question and mocked Gemini response."""
    with patch("qna.get_gemini_client") as mock_get_client:
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "The Pacific Ocean is the largest ocean on Earth."
        mock_model.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_model

        payload = {"text": "What is the largest ocean?"}
        response = client.post("/qa", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "Pacific Ocean" in data["answer"]


def test_qa_empty_input(client):
    """Verifies POST /qa rejects empty question string with 400."""
    response = client.post("/qa", json={"text": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_qa_whitespace_input(client):
    """Verifies POST /qa rejects whitespace-only string with 400."""
    response = client.post("/qa", json={"text": "   "})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_qa_invalid_payload(client):
    """Verifies POST /qa rejects missing 'text' field with 422."""
    response = client.post("/qa", json={"unknown_key": "test"})
    assert response.status_code == 422


def test_qa_api_failure_handled(client):
    """Verifies POST /qa handles Gemini API failure gracefully with 500 and clean message."""
    with patch("qna.get_gemini_client") as mock_get_client:
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API connection timeout")
        mock_get_client.return_value = mock_model

        response = client.post("/qa", json={"text": "How do stars form?"})
        assert response.status_code == 500
        assert "Something went wrong" in response.json()["detail"]


# =====================================================================
# 3. Feature 2: /explain Tests
# =====================================================================

def test_explain_valid_topic(client):
    """Verifies POST /explain generates beginner-friendly explanation structure."""
    payload = {"topic": "Pythagoras theorem"}
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert "topic" in data
    assert data["topic"] == "Pythagoras theorem"
    assert len(data["explanation"]) > 30


def test_explain_with_text_field(client):
    """Verifies POST /explain accepts 'text' alternative field."""
    payload = {"text": "Binary Search"}
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Binary Search"


def test_explain_empty_topic(client):
    """Verifies POST /explain rejects empty topic with 400."""
    response = client.post("/explain", json={"topic": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


# =====================================================================
# 4. Feature 3: /quiz Tests
# =====================================================================

def test_quiz_valid_input_structure(client):
    """
    Verifies POST /quiz returns exactly 3 MCQs, each with 4 options and 1 correct answer.
    """
    payload = {"topic": "Photosynthesis"}
    response = client.post("/quiz", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    questions = data["questions"]
    assert len(questions) == 3

    for q in questions:
        assert "question" in q
        assert "options" in q
        assert "correct_answer" in q
        assert len(q["options"]) == 4
        assert q["correct_answer"] in q["options"]


def test_quiz_empty_input(client):
    """Verifies POST /quiz rejects empty input with 400."""
    response = client.post("/quiz", json={"topic": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_quiz_mocked_gemini_json(client):
    """Verifies POST /quiz parses custom JSON returned by Gemini."""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda k, default="": "mock_valid_key" if k == "GEMINI_API_KEY" else default
        with patch("google.generativeai.GenerativeModel") as mock_gen_model:
            mock_instance = MagicMock()
            mock_res = MagicMock()
            mock_res.text = """
            ```json
            {
              "questions": [
                {
                  "question": "What is photosynthesis?",
                  "options": [
                    "Process of respiration",
                    "Process by which plants make food",
                    "Process of digestion",
                    "Process of reproduction"
                  ],
                  "correct_answer": "Process by which plants make food"
                },
                {
                  "question": "What gas do plants absorb during photosynthesis?",
                  "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
                  "correct_answer": "Carbon dioxide"
                },
                {
                  "question": "What pigment absorbs sunlight in plant cells?",
                  "options": ["Hemoglobin", "Melanin", "Chlorophyll", "Carotene"],
                  "correct_answer": "Chlorophyll"
                }
              ]
            }
            ```
            """
            mock_instance.generate_content.return_value = mock_res
            mock_gen_model.return_value = mock_instance

            response = client.post("/quiz", json={"text": "Photosynthesis process in plants"})
            assert response.status_code == 200
            data = response.json()
            assert len(data["questions"]) == 3
            assert data["questions"][0]["correct_answer"] == "Process by which plants make food"


# =====================================================================
# 5. Feature 4: /summarize Tests
# =====================================================================

def test_summarize_valid_input_mocked(client):
    """Verifies POST /summarize condenses educational text."""
    with patch("summary_module.os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda k, default="": "mock_api_key" if k == "GEMINI_API_KEY" else default
        with patch("google.generativeai.GenerativeModel") as mock_model_cls:
            mock_model = MagicMock()
            mock_res = MagicMock()
            mock_res.text = (
                "**Core Summary**: The solar system consists of the Sun and celestial bodies orbiting it.\n"
                "**Key Takeaways**:\n- 8 major planets\n- Sun holds majority of mass"
            )
            mock_model.generate_content.return_value = mock_res
            mock_model_cls.return_value = mock_model

            long_text = (
                "The solar system consists of the Sun and the objects that orbit it, either directly "
                "or indirectly. Of the objects that orbit the Sun directly, the largest are the eight "
                "planets, with the remainder being smaller objects, such as dwarf planets and small bodies."
            )
            response = client.post("/summarize", json={"text": long_text})
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "solar system" in data["summary"].lower()


def test_summarize_empty_input(client):
    """Verifies POST /summarize rejects empty string with 400."""
    response = client.post("/summarize", json={"text": ""})
    assert response.status_code == 400


def test_summarize_api_error_handling(client):
    """Verifies POST /summarize handles upstream exceptions gracefully with 500."""
    with patch("summary_module.os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda k, default="": "mock_api_key" if k == "GEMINI_API_KEY" else default
        with patch("google.generativeai.GenerativeModel") as mock_model_cls:
            mock_model = MagicMock()
            mock_model.generate_content.side_effect = Exception("Quota exceeded")
            mock_model_cls.return_value = mock_model

            response = client.post("/summarize", json={"text": "Test passage content"})
            assert response.status_code == 500
            assert "Something went wrong" in response.json()["detail"]


# =====================================================================
# 6. Feature 5: /learn/recommendations Tests
# =====================================================================

def test_learning_path_valid_topic(client):
    """Verifies POST /learn/recommendations generates structured beginner-to-advanced roadmap."""
    payload = {"topic": "SQL"}
    response = client.post("/learn/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "topic" in data
    assert "learning_path" in data
    path = data["learning_path"]
    assert "beginner" in path
    assert "intermediate" in path
    assert "advanced" in path
    assert "timeline" in data
    assert "learning_objectives" in data
    assert "practice_suggestions" in data
    assert "recommended_resources" in data


def test_learning_path_empty_topic(client):
    """Verifies POST /learn/recommendations rejects empty topic with 400."""
    response = client.post("/learn/recommendations", json={"topic": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
