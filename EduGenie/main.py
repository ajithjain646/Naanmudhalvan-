"""
EduGenie – AI-Powered Learning Assistant
Main FastAPI Application Server
Provides REST API endpoints for QA, concept explanation, quiz generation,
summarization, and personalized learning paths, along with the interactive web UI.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# Import EduGenie AI Feature Modules
from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import generate_learning_path

# Load environment configuration
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("edugenie.main")

# Initialize FastAPI application
app = FastAPI(
    title="EduGenie – AI-Powered Learning Assistant",
    description="A complete full-stack AI educational assistant for students and self-learners.",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ---------------------------------------------------------
# Request Models & Validation
# ---------------------------------------------------------

class QARequest(BaseModel):
    text: str = Field(..., description="The student's question to answer")

    def get_text(self) -> str:
        cleaned = self.text.strip() if self.text else ""
        if not cleaned:
            raise ValueError("Question cannot be empty or only whitespace.")
        return cleaned


class ExplainRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic or concept to explain")
    text: Optional[str] = Field(None, description="Alternative field for topic")

    def get_topic(self) -> str:
        val = self.topic or self.text or ""
        cleaned = val.strip()
        if not cleaned:
            raise ValueError("Topic to explain cannot be empty.")
        return cleaned


class QuizRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic for the quiz")
    text: Optional[str] = Field(None, description="Educational passage or topic")

    def get_topic_or_text(self) -> str:
        val = self.topic or self.text or ""
        cleaned = val.strip()
        if not cleaned:
            raise ValueError("Topic or educational passage cannot be empty.")
        return cleaned


class SummaryRequest(BaseModel):
    text: str = Field(..., description="Educational passage or article to summarize")

    def get_text(self) -> str:
        cleaned = self.text.strip() if self.text else ""
        if not cleaned:
            raise ValueError("Passage to summarize cannot be empty or only whitespace.")
        return cleaned


class LearningPathRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Subject or technology to learn")
    text: Optional[str] = Field(None, description="Alternative field for topic")

    def get_topic(self) -> str:
        val = self.topic or self.text or ""
        cleaned = val.strip()
        if not cleaned:
            raise ValueError("Topic for learning path cannot be empty.")
        return cleaned


# ---------------------------------------------------------
# Global Exception Handlers
# ---------------------------------------------------------

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handles validation and parameter errors cleanly with 400 Bad Request."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "error": "Bad Request"}
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """Handles runtime AI failures gracefully with 500 Internal Server Error."""
    logger.error(f"Runtime failure: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "error": "Service Error"}
    )


# ---------------------------------------------------------
# Frontend Routes
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse, summary="EduGenie Dashboard")
async def read_root(request: Request):
    """Renders the main EduGenie educational dashboard interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "EduGenie – AI-Powered Learning Assistant",
            "app_name": "EduGenie"
        }
    )


@app.get("/health", summary="Health Check")
async def health_check():
    """Returns application status and checks if GEMINI_API_KEY is configured."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    has_key = bool(api_key and api_key != "your_api_key_here")
    return {
        "status": "healthy",
        "app": "EduGenie",
        "gemini_configured": has_key
    }


# ---------------------------------------------------------
# Feature 1: Ask Questions (AI Q&A)
# ---------------------------------------------------------

@app.post("/qa", summary="Ask a question")
async def qa_endpoint(payload: QARequest):
    """
    POST /qa
    Answers a student question accurately, concisely, and clearly using Google Gemini.
    """
    try:
        text = payload.get_text()
        result = answer_question(text)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /qa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating your response. Please try again."
        )


# ---------------------------------------------------------
# Feature 2: Explain a Concept
# ---------------------------------------------------------

@app.post("/explain", summary="Explain a concept for beginners")
async def explain_endpoint(payload: ExplainRequest):
    """
    POST /explain
    Explains a concept with simple definition, step-by-step breakdown,
    example, and important points using a local language model (LaMini-Flan-T5).
    """
    try:
        topic = payload.get_topic()
        result = explain_concept(topic)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /explain: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating the concept explanation. Please try again."
        )


# ---------------------------------------------------------
# Feature 3: Generate Quiz
# ---------------------------------------------------------

@app.post("/quiz", summary="Generate a 3-question multiple-choice quiz")
async def quiz_endpoint(payload: QuizRequest):
    """
    POST /quiz
    Generates exactly 3 MCQs with 4 options each and 1 correct answer as valid JSON.
    """
    try:
        topic_or_text = payload.get_topic_or_text()
        result = generate_quiz(topic_or_text)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating the quiz. Please try again."
        )


# ---------------------------------------------------------
# Feature 4: Summarize Text
# ---------------------------------------------------------

@app.post("/summarize", summary="Summarize an educational passage")
async def summarize_endpoint(payload: SummaryRequest):
    """
    POST /summarize
    Summarizes long educational text into a concise revision-friendly format.
    """
    try:
        text = payload.get_text()
        result = summarize_text(text)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /summarize: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating the summary. Please try again."
        )


# ---------------------------------------------------------
# Feature 5: Personalized Learning Path
# ---------------------------------------------------------

@app.post("/learn/recommendations", summary="Generate personalized learning path")
async def learning_path_endpoint(payload: LearningPathRequest):
    """
    POST /learn/recommendations
    Generates a structured learning roadmap from Beginner to Advanced with
    timeline, objectives, practice suggestions, and recommended resources.
    """
    try:
        topic = payload.get_topic()
        result = generate_learning_path(topic)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /learn/recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating learning recommendations. Please try again."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
