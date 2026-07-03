

<p align="center">
  <img src="Screenshot%202026-07-03%20195401.png" alt="FitGenie AI Dashboard" width="100%">
</p>

<h1 align="center">🏋️ FitGenie AI</h1>

<p align="center">
  <strong>Forged, Not Found.</strong><br>
  <em>AI-Powered Fitness Assistant — Personalized Coaching Through Artificial Intelligence</em>
</p>

<p align="center">
  <a href="https://fitgenie-teaw.onrender.com">
    <img src="https://img.shields.io/badge/Live-Demo-10b981?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo">
  </a>
  <a href="https://github.com/yourusername/FitGenie">
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11">
  </a>
  <a href="https://flask.palletsprojects.com/">
    <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask 3.0">
  </a>
  <a href="https://groq.com">
    <img src="https://img.shields.io/badge/Groq-Llama%203.3%2070B-f97316?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptMCAxOGMtNC40MSAwLTgtMy41OS04LThzMy41OS04IDgtOCA4IDMuNTkgOCA4LTMuNTkgOC04IDh6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==" alt="Groq">
  </a>
  <a href="https://langchain.com">
    <img src="https://img.shields.io/badge/LangChain-✓-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
  </a>
</p>

---

## ✦ Overview

**FitGenie AI** is an intelligent fitness assistant that delivers **real-time, personalized coaching** powered by Large Language Models and Retrieval-Augmented Generation (RAG). Unlike generic fitness apps, FitGenie adapts to your body, goals, experience level, and even medical conditions — then answers any fitness question like a world-class personal trainer.

> **Live:** [fitgenie-teaw.onrender.com](https://fitgenie-teaw.onrender.com)

---

## ✦ Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Authentication** | Secure registration/login with password hashing & session management |
| 👤 **Fitness Profile** | Age, height, weight, gender, goals, fitness level, medical conditions |
| 📊 **BMI Calculator** | Instant calculation with health category & personalized advice |
| 🤖 **AI Chat** | Context-aware conversations powered by Groq Llama 3.3 70B |
| 📚 **RAG Engine** | Retrieval-Augmented Generation from uploaded fitness documents |
| 📁 **Document Upload** | Upload PDF/TXT files to expand the AI's knowledge base |
| 💬 **Chat History** | Browse, search, and clear past conversations |
| 🌙 **Dark Theme UI** | Modern, responsive interface with Material Icons |

---

## ✦ Tech Stack

```
Frontend          Backend            AI & ML               Data & Storage
─────────────────────────────────────────────────────────────────────────
HTML5             Python 3.11        Groq Llama 3.3 70B    ChromaDB (Vector)
CSS3 (Dark)       Flask 3.0          LangChain Core        SQLite (Relational)
Vanilla JS        Flask-Login        HuggingFace Embed.    SQLAlchemy ORM
Material Icons    Werkzeug           RAG Pipeline          File System
```

### AI Architecture (3-Tier Fallback)

```
   User Question
        │
   ┌────▼────┐
   │  RAG    │  Tier 1 — Vector store + LLM (best answers)
   │ Pipeline│
   └────┬────┘
        │ (if unavailable)
   ┌────▼────┐
   │  LLM    │  Tier 2 — Groq Llama 3.3 only (no documents)
   │  Only   │
   └────┬────┘
        │ (if no API key)
   ┌────▼────────┐
   │  Rule-Based  │  Tier 3 — Keyword-matched fallback (offline mode)
   │  Fallback    │
   └─────────────┘
```

---

## ✦ Quick Start

### Prerequisites
- Python 3.11+
- Groq API key (free at [console.groq.com](https://console.groq.com/keys))

### Setup

```bash
# 1. Clone & enter
git clone https://github.com/yourusername/FitGenie.git
cd FitGenie

# 2. Virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
# Create .env with:
GROQ_API_KEY=gsk_your_key_here
SECRET_KEY=your_random_secret
DATABASE_URL=sqlite:///database.db

# 5. Run
python app.py
```

Visit **http://127.0.0.1:5000** 🚀

---

## ✦ Usage

### User Journey

```
Register → Login → Set Profile → Dashboard → Chat with AI → Achieve Goals
```

### Example Questions

| Category | Questions |
|----------|-----------|
| 💪 **Workouts** | "Create a beginner workout plan" / "How to build muscle fast?" |
| 🥗 **Nutrition** | "Suggest a healthy breakfast for weight loss" / "What foods are high in protein?" |
| 💧 **Hydration** | "How much water should I drink daily?" |
| 📊 **BMI** | "What is my BMI and what does it mean?" |

### RAG Enhancement

Upload your own PDF or TXT files (fitness guides, nutrition research, exercise manuals) and FitGenie will index them into ChromaDB — making the AI **smarter with your specific knowledge base**.

---

## ✦ Deployment

### Render (recommended)

```bash
# runtime.txt
python-3.11.7

# render-build.sh (auto-runs on deploy)
pip install -r requirements.txt
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Production WSGI

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

---

## ✦ Project Structure

```
FitGenie/
├── app.py                 # Flask application (routes, RAG pipeline, AI logic)
├── requirements.txt       # Python dependencies
├── runtime.txt            # Python version for Render
├── render-build.sh        # Render build script
├── .env                   # Environment variables
├── database.db            # SQLite database (auto-created)
├── Screenshot*.png        # App preview image
│
├── templates/             # Jinja2 HTML templates
│   ├── index.html         # Landing page ("Forged, Not Found")
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Main SPA dashboard
│   └── profile.html       # Profile settings
│
├── static/
│   ├── style.css          # Complete dark-theme stylesheet
│   └── app.js             # Frontend JavaScript (SPA logic, chat, BMI, uploads)
│
├── documents/             # PDF/TXT files for RAG ingestion
├── vectorstore/           # ChromaDB persistent vector index
│
├── DEPLOY.md              # Deployment guide
└── README.md              # You are here
```

---

## ✦ How RAG Works

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Load PDFs   │ →  │  Split into  │ →  │  Embed &     │ →  │  Semantic    │
│  & TXT files │    │  500-char    │    │  Store in    │    │  Search      │
│              │    │  chunks (100 │    │  ChromaDB    │    │  (top 3      │
│              │    │  overlap)    │    │              │    │  chunks)     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                   │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  Personalized│ ←  │  LLM         │ ←  │  Chunks +    │ ←────────┘
│  Response    │    │  (Groq)      │    │  Question +  │
│              │    │              │    │  History     │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## ✦ Offline Mode

No API key? No problem. FitGenie runs in **fallback mode** with rule-based responses:
- All auth, profile, and BMI features work
- Chat returns intelligent keyword-matched answers
- Document upload still operates (RAG activates once an API key is set)

---

## ✦ Roadmap

| Quarter | Feature |
|---------|---------|
| ✅ **Current** | AI Chat + RAG + Profile + BMI + Docs |
| 🔜 **Q3 2025** | Voice Assistant (hands-free coaching) |
| 🔜 **Q4 2025** | Progress Charts & Analytics (weight/BMI trends) |
| 🔜 **Q1 2026** | Exercise Video Detection (form correction) |
| 🔜 **Q2 2026** | Mobile App (Flutter/React Native) |
| 🔮 **Future** | AI Trainer Avatar, PDF Reports, Calorie Prediction |

---

<p align="center">
  <strong>FitGenie AI</strong> — <em>Forged, Not Found.</em><br>
  Built with Flask, LangChain, Groq & ChromaDB
</p>

<p align="center">
  <a href="https://fitgenie-teaw.onrender.com">🌐 Live Demo</a>
</p>
