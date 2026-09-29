/**
 * EduGenie – AI-Powered Learning Assistant Frontend Script
 * Handles task switching, interactive API communication with FastAPI,
 * quiz progression, and result card rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const navTabs = document.querySelectorAll(".nav-tab");
    const taskSelect = document.getElementById("task-select");
    const taskHeading = document.getElementById("task-heading");
    const taskInstruction = document.getElementById("task-instruction");
    const userInput = document.getElementById("user-input");
    const btnSubmit = document.getElementById("btn-submit");
    const btnSubmitText = document.getElementById("btn-submit-text");
    const btnClear = document.getElementById("btn-clear");
    const charCount = document.getElementById("char-count");
    const samplesContainer = document.getElementById("samples-container");
    const errorBanner = document.getElementById("error-banner");
    const errorMessage = document.getElementById("error-message");
    const btnCloseError = document.getElementById("btn-close-error");
    const loadingSpinner = document.getElementById("loading-spinner");
    const loadingTitle = document.getElementById("loading-title");
    const loadingSubtitle = document.getElementById("loading-subtitle");
    const resultContainer = document.getElementById("result-container");
    const edugenieForm = document.getElementById("edugenie-form");

    // Task Configurations & Example Samples
    const taskConfigs = {
        qa: {
            title: "Ask an Educational Question",
            instruction: "Get concise, accurate, and student-friendly answers for any academic query.",
            placeholder: "Enter your question here (e.g., 'What is the largest ocean?')",
            buttonText: "Ask EduGenie",
            endpoint: "/qa",
            requestKey: "text",
            loadingTitle: "EduGenie is finding the answer...",
            samples: [
                "What is the largest ocean?",
                "Why is the sky blue?",
                "How does gravity work?"
            ]
        },
        explain: {
            title: "Explain a Concept (Local Model)",
            instruction: "Break down complex topics into simple definitions, step-by-step logic, examples, and key takeaways.",
            placeholder: "Enter the concept to explain (e.g., 'Explain the Pythagoras theorem.')",
            buttonText: "Explain Concept",
            endpoint: "/explain",
            requestKey: "topic",
            loadingTitle: "Local Model is simplifying the concept...",
            samples: [
                "Pythagoras theorem",
                "Binary search algorithm",
                "Photosynthesis"
            ]
        },
        quiz: {
            title: "Generate Interactive Quiz",
            instruction: "Create a 3-question multiple-choice quiz based on any topic or educational text passage.",
            placeholder: "Enter a topic or paste a passage (e.g., 'Photosynthesis is the process by which green plants...')",
            buttonText: "Generate 3-Question Quiz",
            endpoint: "/quiz",
            requestKey: "text",
            loadingTitle: "Generating 3 MCQs with answer keys...",
            samples: [
                "Photosynthesis",
                "Solar System",
                "Python Data Structures"
            ]
        },
        summarize: {
            title: "Summarize Educational Text",
            instruction: "Condense long academic articles, passages, or textbook excerpts into high-yield revision notes.",
            placeholder: "Paste the long educational paragraph or article here to summarize...",
            buttonText: "Summarize Text",
            endpoint: "/summarize",
            requestKey: "text",
            loadingTitle: "EduGenie is synthesizing key points...",
            samples: [
                "The solar system consists of the Sun and the objects that orbit it, either directly or indirectly. Of the objects that orbit the Sun directly, the largest are the four gas and ice giants and the four terrestrial planets, followed by an unknown number of dwarf planets and innumerable small Solar System bodies.",
                "Machine learning is an umbrella term for solving problems for which the development of algorithms by human programmers would be cost-prohibitive, and instead the problems are solved by helping machines 'learn' from data. The machine learning lifecycle typically involves data collection, feature engineering, model training, and evaluation."
            ]
        },
        learn: {
            title: "Personalized Learning Path",
            instruction: "Generate a structured curriculum from Beginner to Advanced with timelines, objectives, practice, and resources.",
            placeholder: "Enter a technology or subject (e.g., 'SQL', 'FastAPI', 'Cybersecurity')",
            buttonText: "Generate Learning Path",
            endpoint: "/learn/recommendations",
            requestKey: "topic",
            loadingTitle: "Curating personalized learning roadmap...",
            samples: [
                "SQL",
                "Machine Learning",
                "Full Stack Web Development"
            ]
        }
    };

    let currentTask = "qa";

    // Quiz State Management
    let quizData = [];
    let currentQuizIndex = 0;
    let quizScore = 0;
    let selectedOptionIndex = null;
    let answerSubmitted = false;

    // Initialize UI
    function updateTaskView(taskKey) {
        currentTask = taskKey;
        const config = taskConfigs[taskKey];

        // Sync tabs
        navTabs.forEach(tab => {
            if (tab.dataset.task === taskKey) {
                tab.classList.add("active");
            } else {
                tab.classList.remove("active");
            }
        });

        // Sync dropdown
        if (taskSelect.value !== taskKey) {
            taskSelect.value = taskKey;
        }

        // Update form elements
        taskHeading.textContent = config.title;
        taskInstruction.textContent = config.instruction;
        userInput.placeholder = config.placeholder;
        btnSubmitText.textContent = config.buttonText;

        // Render sample chips
        samplesContainer.innerHTML = "";
        config.samples.forEach(sample => {
            const chip = document.createElement("button");
            chip.type = "button";
            chip.className = "sample-chip";
            chip.textContent = sample.length > 40 ? sample.substring(0, 37) + "..." : sample;
            chip.title = sample;
            chip.addEventListener("click", () => {
                userInput.value = sample;
                updateCharCount();
                userInput.focus();
            });
            samplesContainer.appendChild(chip);
        });

        hideError();
        hideLoading();
    }

    // Tab clicks
    navTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            updateTaskView(tab.dataset.task);
        });
    });

    // Dropdown change
    taskSelect.addEventListener("change", (e) => {
        updateTaskView(e.target.value);
    });

    // Character counter
    function updateCharCount() {
        const count = userInput.value.length;
        charCount.textContent = `${count} character${count === 1 ? "" : "s"}`;
    }
    userInput.addEventListener("input", updateCharCount);

    // Clear button
    btnClear.addEventListener("click", () => {
        userInput.value = "";
        updateCharCount();
        userInput.focus();
    });

    // Error alert controls
    function showError(msg) {
        errorMessage.textContent = msg || "An unexpected error occurred. Please try again.";
        errorBanner.classList.remove("hidden");
        errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function hideError() {
        errorBanner.classList.add("hidden");
    }

    btnCloseError.addEventListener("click", hideError);

    // Loading indicator
    function showLoading(customTitle) {
        hideError();
        resultContainer.classList.add("hidden");
        loadingTitle.textContent = customTitle || taskConfigs[currentTask].loadingTitle;
        loadingSpinner.classList.remove("hidden");
        btnSubmit.disabled = true;
    }

    function hideLoading() {
        loadingSpinner.classList.add("hidden");
        btnSubmit.disabled = false;
    }

    // Form submission
    edugenieForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) {
            showError("Please enter some text or select an example before submitting.");
            userInput.focus();
            return;
        }

        const config = taskConfigs[currentTask];
        showLoading(config.loadingTitle);

        try {
            const payload = {};
            payload[config.requestKey] = text;
            // Also supply alternative key for flexibility
            if (config.requestKey === "topic") payload["text"] = text;
            if (config.requestKey === "text") payload["topic"] = text;

            const response = await fetch(config.endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                const detail = data.detail || "Something went wrong while generating your response. Please try again.";
                showError(detail);
                hideLoading();
                return;
            }

            hideLoading();
            renderResponse(currentTask, data, text);

        } catch (err) {
            console.error("EduGenie request error:", err);
            hideLoading();
            showError("Unable to communicate with the server. Please ensure the backend is running.");
        }
    });

    // ---------------------------------------------------------
    // Render Results by Task Type
    // ---------------------------------------------------------
    function renderResponse(task, data, query) {
        resultContainer.innerHTML = "";
        resultContainer.classList.remove("hidden");

        switch (task) {
            case "qa":
                renderQAResult(data, query);
                break;
            case "explain":
                renderExplainResult(data, query);
                break;
            case "quiz":
                initInteractiveQuiz(data);
                break;
            case "summarize":
                renderSummaryResult(data, query);
                break;
            case "learn":
                renderLearningPathResult(data, query);
                break;
            default:
                renderGenericResult(data);
        }

        resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // 1. Q&A Renderer
    function renderQAResult(data, query) {
        const answerText = data.answer || "No answer generated.";
        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `
            <div class="result-header">
                <div class="result-title-group">
                    <span class="result-badge">Q&amp;A Answer</span>
                    <h3 class="result-heading">AI Response</h3>
                </div>
                <div class="result-actions">
                    <button class="btn-secondary" onclick="navigator.clipboard.writeText('${escapeQuotes(answerText)}')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                        Copy
                    </button>
                </div>
            </div>
            <div class="result-body prose">
                <p><strong>Question:</strong> ${escapeHtml(query)}</p>
                <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 16px 0;">
                <p style="white-space: pre-wrap; font-size: 1.05rem; line-height: 1.6;">${formatMarkdown(answerText)}</p>
            </div>
        `;
        resultContainer.appendChild(card);
    }

    // 2. Explain Concept Renderer
    function renderExplainResult(data, query) {
        const explanation = data.explanation || "";
        const topic = data.topic || query;
        const modelUsed = data.model_used || "LaMini-Flan-T5 (Local Model)";

        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `
            <div class="result-header">
                <div class="result-title-group">
                    <span class="result-badge local-model">${escapeHtml(modelUsed)}</span>
                    <h3 class="result-heading">Concept: ${escapeHtml(topic)}</h3>
                </div>
                <div class="result-actions">
                    <button class="btn-secondary" onclick="navigator.clipboard.writeText('${escapeQuotes(explanation)}')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                        Copy
                    </button>
                </div>
            </div>
            <div class="result-body prose">
                ${formatMarkdown(explanation)}
            </div>
        `;
        resultContainer.appendChild(card);
    }

    // 3. Interactive Quiz Flow
    function initInteractiveQuiz(data) {
        if (!data || !data.questions || !Array.isArray(data.questions) || data.questions.length === 0) {
            showError("Quiz generation returned invalid data. Please try again.");
            return;
        }

        quizData = data.questions;
        currentQuizIndex = 0;
        quizScore = 0;
        selectedOptionIndex = null;
        answerSubmitted = false;

        renderQuizStep();
    }

    function renderQuizStep() {
        resultContainer.innerHTML = "";
        const total = quizData.length;

        // If finished all questions, render Final Score Card
        if (currentQuizIndex >= total) {
            renderQuizScoreCard();
            return;
        }

        const q = quizData[currentQuizIndex];
        const percent = Math.round(((currentQuizIndex) / total) * 100);

        const quizWrapper = document.createElement("div");
        quizWrapper.className = "quiz-wrapper";

        quizWrapper.innerHTML = `
            <div class="quiz-header">
                <span class="quiz-progress-label">Question ${currentQuizIndex + 1} of ${total}</span>
                <div class="quiz-progress-bar">
                    <div class="quiz-progress-fill" style="width: ${percent}%;"></div>
                </div>
            </div>
            <div class="quiz-card">
                <div class="quiz-question-number">Multiple Choice Question</div>
                <h3 class="quiz-question-title">${escapeHtml(q.question)}</h3>

                <div class="quiz-options" id="quiz-options-container">
                    ${q.options.map((opt, i) => `
                        <button type="button" class="quiz-option" data-index="${i}">
                            <span class="quiz-option-radio"></span>
                            <span class="quiz-option-text">${escapeHtml(opt)}</span>
                        </button>
                    `).join("")}
                </div>

                <div id="quiz-feedback-box"></div>

                <div class="quiz-footer">
                    <button type="button" id="btn-quiz-action" class="btn-primary" disabled>
                        <span>Submit Answer</span>
                    </button>
                </div>
            </div>
        `;

        resultContainer.appendChild(quizWrapper);

        // Attach event handlers to options
        const optionBtns = quizWrapper.querySelectorAll(".quiz-option");
        const btnAction = quizWrapper.querySelector("#btn-quiz-action");
        const feedbackBox = quizWrapper.querySelector("#quiz-feedback-box");

        selectedOptionIndex = null;
        answerSubmitted = false;

        optionBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                if (answerSubmitted) return;

                optionBtns.forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
                selectedOptionIndex = parseInt(btn.dataset.index, 10);
                btnAction.disabled = false;
            });
        });

        // Action button click: Submit Answer OR Next Question
        btnAction.addEventListener("click", () => {
            if (!answerSubmitted) {
                // Submit Answer Step
                if (selectedOptionIndex === null) return;
                answerSubmitted = true;

                const chosenOption = q.options[selectedOptionIndex];
                const isCorrect = chosenOption.trim().toLowerCase() === q.correct_answer.trim().toLowerCase();

                // Highlight correct and incorrect options
                optionBtns.forEach((b, idx) => {
                    b.disabled = true;
                    const optText = q.options[idx].trim().toLowerCase();
                    if (optText === q.correct_answer.trim().toLowerCase()) {
                        b.classList.add("correct");
                    } else if (idx === selectedOptionIndex && !isCorrect) {
                        b.classList.add("incorrect");
                    }
                });

                if (isCorrect) {
                    quizScore++;
                    feedbackBox.innerHTML = `
                        <div class="quiz-feedback success">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                            <span>Correct! Well done.</span>
                        </div>
                    `;
                } else {
                    feedbackBox.innerHTML = `
                        <div class="quiz-feedback error">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                            <span>Incorrect. The correct answer is: <strong>${escapeHtml(q.correct_answer)}</strong></span>
                        </div>
                    `;
                }

                // Update action button for next step
                const isLastQuestion = currentQuizIndex === total - 1;
                btnAction.innerHTML = isLastQuestion 
                    ? `<span>View Final Score</span> <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>`
                    : `<span>Next Question</span> <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>`;

            } else {
                // Advance to next question
                currentQuizIndex++;
                renderQuizStep();
            }
        });
    }

    function renderQuizScoreCard() {
        const total = quizData.length;
        const percent = Math.round((quizScore / total) * 100);
        let feedbackMsg = "Keep practicing! You can always try again.";
        if (quizScore === total) {
            feedbackMsg = "Outstanding! Perfect score! You have mastered this concept.";
        } else if (quizScore >= total / 2) {
            feedbackMsg = "Great effort! A solid performance with good understanding.";
        }

        const scoreCard = document.createElement("div");
        scoreCard.className = "result-card quiz-results-card";
        scoreCard.innerHTML = `
            <div class="score-circle">
                <span class="score-number">${quizScore}</span>
                <span class="score-total">of ${total}</span>
            </div>
            <h2 class="score-heading">Quiz Completed!</h2>
            <p class="score-message">Your score: <strong>${quizScore} / ${total} (${percent}%)</strong>. ${feedbackMsg}</p>
            <div>
                <button type="button" class="btn-primary" id="btn-quiz-retry">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                    <span>Try Again</span>
                </button>
            </div>
        `;

        resultContainer.appendChild(scoreCard);

        scoreCard.querySelector("#btn-quiz-retry").addEventListener("click", () => {
            currentQuizIndex = 0;
            quizScore = 0;
            renderQuizStep();
        });
    }

    // 4. Summarization Renderer
    function renderSummaryResult(data, originalText) {
        const summary = data.summary || "No summary generated.";
        const origWords = originalText.trim().split(/\s+/).length;
        const summWords = summary.trim().split(/\s+/).length;
        const reduction = origWords > 0 ? Math.max(0, Math.round(((origWords - summWords) / origWords) * 100)) : 0;

        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `
            <div class="result-header">
                <div class="result-title-group">
                    <span class="result-badge">Summary</span>
                    <h3 class="result-heading">Concise Revision Summary</h3>
                </div>
                <div class="result-actions">
                    <button class="btn-secondary" onclick="navigator.clipboard.writeText('${escapeQuotes(summary)}')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                        Copy
                    </button>
                </div>
            </div>
            <div class="result-body">
                <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
                    <span class="overview-pill">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                        Original: ${origWords} words
                    </span>
                    <span class="overview-pill">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                        Summary: ${summWords} words
                    </span>
                    <span class="overview-pill" style="color: var(--success);">
                        ⚡ ${reduction}% Condensed
                    </span>
                </div>
                <div class="prose">
                    ${formatMarkdown(summary)}
                </div>
            </div>
        `;
        resultContainer.appendChild(card);
    }

    // 5. Personalized Learning Path Renderer
    function renderLearningPathResult(data, topic) {
        const pathData = data.learning_path || {};
        const timeline = data.timeline || "Self-Paced";
        const objectives = data.learning_objectives || [];
        const practice = data.practice_suggestions || [];
        const resources = data.recommended_resources || [];

        const card = document.createElement("div");
        card.className = "result-card";
        card.innerHTML = `
            <div class="result-header">
                <div class="result-title-group">
                    <span class="result-badge">Roadmap</span>
                    <h3 class="result-heading">Learning Path: ${escapeHtml(data.topic || topic)}</h3>
                </div>
            </div>
            <div class="result-body path-wrapper">
                
                <!-- Timeline & High-level stats -->
                <div class="path-overview">
                    <span class="overview-pill">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        Timeline: <strong>${escapeHtml(timeline)}</strong>
                    </span>
                    <span class="overview-pill">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                        3 Mastery Stages
                    </span>
                </div>

                <!-- Learning Objectives -->
                ${objectives.length > 0 ? `
                    <div class="path-section-box">
                        <h4 class="section-box-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
                            Key Learning Objectives
                        </h4>
                        <ul class="prose" style="margin: 0; padding-left: 20px;">
                            ${objectives.map(obj => `<li>${escapeHtml(obj)}</li>`).join("")}
                        </ul>
                    </div>
                ` : ""}

                <!-- 3 Stages: Beginner, Intermediate, Advanced -->
                <div class="path-stages-grid">
                    <!-- Beginner Stage -->
                    <div class="stage-card">
                        <div class="stage-header">
                            <h4 style="font-weight: 800; font-size: 1rem;">1. Beginner</h4>
                            <span class="stage-badge beginner">Foundation</span>
                        </div>
                        <ul class="stage-concepts">
                            ${renderStageConcepts(pathData.beginner)}
                        </ul>
                    </div>

                    <!-- Intermediate Stage -->
                    <div class="stage-card">
                        <div class="stage-header">
                            <h4 style="font-weight: 800; font-size: 1rem;">2. Intermediate</h4>
                            <span class="stage-badge intermediate">Application</span>
                        </div>
                        <ul class="stage-concepts">
                            ${renderStageConcepts(pathData.intermediate)}
                        </ul>
                    </div>

                    <!-- Advanced Stage -->
                    <div class="stage-card">
                        <div class="stage-header">
                            <h4 style="font-weight: 800; font-size: 1rem;">3. Advanced</h4>
                            <span class="stage-badge advanced">Mastery</span>
                        </div>
                        <ul class="stage-concepts">
                            ${renderStageConcepts(pathData.advanced)}
                        </ul>
                    </div>
                </div>

                <!-- Practice Suggestions -->
                ${practice.length > 0 ? `
                    <div class="path-section-box">
                        <h4 class="section-box-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                            Practice Exercises &amp; Projects
                        </h4>
                        <ul class="prose" style="margin: 0; padding-left: 20px;">
                            ${practice.map(item => `<li>${escapeHtml(item)}</li>`).join("")}
                        </ul>
                    </div>
                ` : ""}

                <!-- Recommended Resources -->
                ${resources.length > 0 ? `
                    <div class="path-section-box">
                        <h4 class="section-box-title">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                            Recommended Resources
                        </h4>
                        <div class="resources-grid">
                            ${resources.map(res => `
                                <a href="${escapeHtml(res.url || '#')}" target="_blank" rel="noopener noreferrer" class="resource-card">
                                    <div class="resource-type">${escapeHtml(res.type || 'Resource')}</div>
                                    <div class="resource-name">${escapeHtml(res.name || 'Learn More')} &rarr;</div>
                                </a>
                            `).join("")}
                        </div>
                    </div>
                ` : ""}

            </div>
        `;
        resultContainer.appendChild(card);
    }

    function renderStageConcepts(stageItems) {
        if (!stageItems || !Array.isArray(stageItems) || stageItems.length === 0) {
            return `<li>No specific concepts listed</li>`;
        }
        return stageItems.map(item => {
            if (typeof item === "string") {
                return `
                    <li class="stage-concept-item">
                        <div class="stage-concept-title">${escapeHtml(item)}</div>
                    </li>
                `;
            }
            return `
                <li class="stage-concept-item">
                    <div class="stage-concept-title">${escapeHtml(item.title || item.name || "")}</div>
                    ${item.description ? `<div class="stage-concept-desc">${escapeHtml(item.description)}</div>` : ""}
                </li>
            `;
        }).join("");
    }

    // Helper Utilities
    function escapeHtml(text) {
        if (!text) return "";
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function escapeQuotes(str) {
        if (!str) return "";
        return String(str)
            .replace(/\\/g, "\\\\")
            .replace(/'/g, "\\'")
            .replace(/"/g, '\\"')
            .replace(/\n/g, "\\n")
            .replace(/\r/g, "");
    }

    function formatMarkdown(text) {
        if (!text) return "";
        let html = escapeHtml(text);
        
        // Headings ###
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2 style="font-size:1.25rem; font-weight:700; margin:16px 0 8px;">$1</h2>');
        
        // Bold **text**
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Inline code `code`
        html = html.replace(/`([^`]+)`/g, '<code style="background:var(--bg-subtle); padding:2px 6px; border-radius:4px; font-family:monospace; font-size:0.88em;">$1</code>');

        // Bullet lists
        html = html.replace(/^\s*[-*]\s+(.*)$/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Numbered lists
        html = html.replace(/^\s*\d+\.\s+(.*)$/gim, '<li>$1</li>');

        // Line breaks
        html = html.replace(/\n\n/g, '</p><p>');

        return `<p>${html}</p>`;
    }

    // Initialize default view
    updateTaskView("qa");
});
