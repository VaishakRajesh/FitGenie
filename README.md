# FitGenie AI

> AI-Powered Fitness Assistant built with Flask, LangChain & RAG

FitGenie AI is an intelligent fitness assistant that provides personalized workout plans, nutrition guidance, BMI analysis, and answers fitness-related questions using a Large Language Model (LLM) with Retrieval-Augmented Generation (RAG).

## Tech Stack

- **Backend:** Python, Flask
- **AI:** OpenAI GPT, LangChain
- **RAG:** ChromaDB, HuggingFace Embeddings
- **Database:** SQLite with SQLAlchemy
- **Frontend:** HTML, CSS, JavaScript

## Features

- ✅ User Registration & Login (secure password hashing)
- ✅ Personalized fitness profiles (age, weight, height, goals)
- ✅ BMI Calculator with health advice
- ✅ AI Chat powered by LangChain + OpenAI
- ✅ RAG (Retrieval-Augmented Generation) from fitness documents
- ✅ Conversation memory for contextual responses
- ✅ Chat history with search
- ✅ Upload custom PDF/TXT documents for knowledge base
- ✅ Responsive dark-theme UI
- ✅ Fallback responses (works without API key)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd FitGenie-AI
```

### 2. Create virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-random-secret-key
```

> **Note:** Without an API key, the app runs in fallback mode with rule-based responses.

### 5. Add fitness documents (optional)

Place PDF or TXT files in the `documents/` folder:
- `fitness.pdf` or `fitness.txt`
- `nutrition.pdf` or `nutrition.txt`
- `exercises.pdf` or `exercises.txt`

Three sample text files are already included to get started.

### 6. Run the application

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

## Usage

1. **Register** a new account at `/register`
2. **Login** at `/login`
3. **Update your profile** - Age, height, weight, fitness goals
4. **Calculate BMI** - Get instant health category and advice
5. **Chat with AI** - Ask fitness questions, get workout plans, diet advice
6. **Upload documents** - Enhance AI knowledge with custom PDFs

### Example questions:

- "Create a beginner workout plan"
- "Suggest a healthy breakfast for weight loss"
- "How to build muscle fast?"
- "What foods are high in protein?"
- "How much water should I drink daily?"

## Project Structure

```
FitGenie-AI/
├── app.py                 # Flask application with all routes and RAG pipeline
├── database.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── templates/
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Main dashboard with all features
│   └── profile.html       # Profile settings page
├── static/
│   ├── style.css          # Complete stylesheet (dark theme)
│   └── app.js             # Frontend JavaScript logic
├── documents/             # Place PDF/TXT files here for RAG
│   ├── fitness.txt
│   ├── nutrition.txt
│   └── exercises.txt
├── vectorstore/           # ChromaDB persists here (auto-created)
└── README.md
```

## How RAG Works

1. Documents are loaded from `documents/` folder
2. Text is split into 500-character chunks (100 overlap)
3. Chunks are embedded using HuggingFace embeddings
4. Embedded vectors stored in ChromaDB (persisted on disk)
5. User question retrieves top 3 relevant chunks
6. LangChain RetrievalQA passes chunks + question to OpenAI GPT
7. LLM generates answer using retrieved context + conversation memory

## Without API Key (Fallback Mode)

If no `OPENAI_API_KEY` is set, the app operates in offline mode:
- All authentication and profile features work
- BMI calculator works
- Chat responds with rule-based answers based on keywords
- Document upload still works but RAG is not active

## Development

Run in debug mode:

```bash
python app.py
```

The server will reload automatically on code changes.

## Production Deployment

Use a production WSGI server:

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

## Future Enhancements

- Voice Assistant integration
- Exercise image/video detection
- Progress graphs and charts
- Calories burned prediction
- Mobile app (Flutter/React Native)
- Admin panel for document management
- AI Trainer avatar
- PDF fitness report generation
