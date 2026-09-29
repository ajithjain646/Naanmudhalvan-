# EduGenie – AI-Powered Learning Assistant

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)
![Google Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**EduGenie** is a full-stack educational assistant web application designed to help students, educators, and self-learners master complex concepts, ask academic questions, generate interactive revision quizzes, summarize lengthy articles, and receive personalized step-by-step learning roadmaps.

The application combines cloud-based LLM intelligence powered by **Google Gemini** with local machine learning capabilities via **LaMini-Flan-T5**, wrapped in a clean, modern, and responsive dashboard interface.

---

## 🌟 Features

EduGenie provides five specialized learning modules:

1. **AI Question & Answer (`POST /qa`)**
   - Ask any academic query or doubt (e.g., *"What is the largest ocean?"*).
   - Powered by **Google Gemini** for concise, factual, and student-friendly answers.

2. **Concept Explanation (`POST /explain`)**
   - Demystifies complex topics (e.g., *"Explain the Pythagoras theorem."*).
   - Powered by a lightweight local model (**LaMini-Flan-T5** via Hugging Face Transformers) with structured educational breakdown:
     - 📌 Simple Definition
     - 🔍 Step-by-Step Explanation
     - 💡 Concrete Example
     - ⚠️ Important Points to Remember

3. **Interactive Quiz Generation (`POST /quiz`)**
   - Automatically generates **exactly 3 multiple-choice questions (MCQs)** with **4 distinct options** and **1 verified correct answer** based on any topic or educational passage.
   - Interactive web UI features step-by-step questions, real-time visual feedback (green/red indicators), score tracking, and a *"Try Again"* review flow.

4. **Text Summarization (`POST /summarize`)**
   - Condenses lengthy educational articles, textbook chapters, or research paragraphs into concise revision summaries.
   - Features structured core summaries, bulleted key takeaways, and word compression statistics.

5. **Personalized Learning Recommendations (`POST /learn/recommendations`)**
   - Enter any technology or subject (e.g., *"SQL"*, *"Machine Learning"*, *"FastAPI"*).
   - Generates a structured multi-stage curriculum:
     - 🟢 **Beginner**: Foundational concepts and syntax
     - 🔵 **Intermediate**: Advanced queries, data flows, and architectures
     - 🟣 **Advanced**: Query optimization, security, and internals
     - ⏱️ Suggested timeline & learning objectives
     - 🛠️ Hands-on practice suggestions & curated learning resources

---

## 🛠️ Technology Stack

### Backend
* **Python 3.10+**
* **FastAPI**: Modern, high-performance web framework for building APIs.
* **Uvicorn**: Lightning-fast ASGI web server implementation.
* **Pydantic**: Robust data validation and settings management.
* **Jinja2**: HTML templating engine for rendering dashboard layouts.
* **python-dotenv**: Environment variable management.

### AI & Machine Learning
* **Google Gemini API**: Powers Q&A, quiz generation, summarization, and curriculum planning.
* **LaMini-Flan-T5 (Local Model)**: Hugging Face text2text pipeline for local concept simplification, with built-in pedagogical fallbacks.

### Frontend
* **HTML5**: Semantic layout with accessible component hierarchy.
* **CSS3**: Responsive flexbox/grid styling, modern color system, smooth transitions, and mobile-friendly typography (Plus Jakarta Sans).
* **Vanilla JavaScript (ES6+)**: Dynamic `fetch()` asynchronous communication, state management for quizzes, and copy utilities without page reloads.

---

## 📁 Project Architecture

```
EduGenie/
├── main.py                     # FastAPI application routes & server configuration
├── explanation_module.py       # Concept explanation engine (LaMini-Flan-T5 / fallback)
├── qna.py                      # Q&A module powered by Google Gemini API
├── quiz_module.py              # 3-MCQ quiz generator with strict JSON schema validation
├── summary_module.py           # Educational text summarization module
├── learning_path.py            # Personalized curriculum and roadmap generator
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variable template
├── .env                        # Local environment configuration (git-ignored)
├── .gitignore                  # Git ignore rules for virtualenvs and secrets
├── README.md                   # Complete documentation
│
├── templates/
│   └── index.html              # Jinja2 dashboard template
│
├── static/
│   ├── style.css               # Clean responsive styles and animations
│   └── script.js               # Interactive client-side logic & quiz engine
│
└── tests/
    └── test_api.py             # Pytest test suite covering all endpoints
```

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.10 or higher installed on your system.
* Internet connection (for Gemini API calls and dependency installation).

### Step 1: Clone or Navigate to the Project Directory

```bash
cd EduGenie
```

### Step 2: Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

EduGenie connects to the Google Gemini API for cloud intelligence.

1. Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *(Or copy manually on Windows: `copy .env.example .env`)*
3. Open `.env` and set your key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere
   ```

> 🔒 **Security Notice**: Your `.env` file contains sensitive credentials and is included in `.gitignore`. Never commit `.env` or hard-code keys into your codebase or frontend JavaScript.

---

## ▶️ Running the Application

Launch the local development server with Uvicorn:

```bash
uvicorn main:app --reload
```

Once started, navigate to your web browser:

👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📖 API Documentation & Endpoints

FastAPI automatically generates interactive, OpenAPI-compliant documentation:

* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc Reference**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Summary of REST Endpoints

| Method | Endpoint | Description | Request Body Example |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Web Dashboard Interface | None |
| `POST` | `/qa` | Ask an educational question | `{"text": "What is the largest ocean?"}` |
| `POST` | `/explain` | Explain a concept for beginners | `{"topic": "Pythagoras theorem"}` |
| `POST` | `/quiz` | Generate 3 MCQs with 4 options | `{"text": "Photosynthesis is the process..."}` |
| `POST` | `/summarize` | Summarize educational passage | `{"text": "Long educational paragraph..."}` |
| `POST` | `/learn/recommendations` | Generate personalized learning roadmap | `{"topic": "SQL"}` |

---

## 🧪 Running Automated Tests

Run the test suite with `pytest`:

```bash
pytest tests/test_api.py -v
```

The tests cover:
- ✅ Successful responses for all 5 core endpoints
- ✅ Input validation (empty, whitespace, missing keys)
- ✅ 3-MCQ schema compliance and JSON parser verification
- ✅ Graceful error handling and safety fallbacks

---

## 🎓 Academic Demonstration Guide

1. **Dashboard & UI**: Open `http://127.0.0.1:8000`. Note the task selector tabs, quick example chips, and clean design.
2. **Q&A Demo**: Click *"What is the largest ocean?"* sample chip and click **Ask EduGenie**.
3. **Concept Explanation**: Switch to **Explain Concept**, click *"Pythagoras theorem"*, and view the structured sections (Definition, Step-by-Step, Example, Key Points).
4. **Interactive Quiz**: Switch to **Generate Quiz**, enter *"Photosynthesis"*, and take the 3-question quiz step-by-step. Select answers to observe immediate green/red feedback and the final score card with *"Try Again"* functionality.
5. **Summarizer**: Switch to **Summarize**, paste an educational passage, and review the word compression stats and key takeaways.
6. **Learning Path**: Switch to **Learning Path**, enter *"SQL"*, and examine the Beginner $\to$ Intermediate $\to$ Advanced roadmap.

---

## 📄 License

This project is licensed under the MIT License.
