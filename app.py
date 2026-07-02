"""
FitGenie AI - AI-Powered Fitness Assistant
Flask + LangChain + RAG + ChromaDB + Groq
"""

# ============================================================
# IMPORTS
# ============================================================
import os
import warnings
from datetime import datetime

# Flask imports
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, session
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# LangChain imports
#
# IMPORTANT: we deliberately avoid importing from the umbrella `langchain`
# package (e.g. `langchain.chains`, `langchain.memory`). That package's
# __init__ chain pulls in a lot of legacy/deprecated modules (APIChain,
# TextRequestsWrapper, etc.) that this app doesn't even use, and those are
# what keep breaking with `ModuleNotFoundError: langchain_core.pydantic_v1`
# whenever langchain-core/langchain-community/langchain drift out of sync.
# Sticking to the narrow, actively-maintained packages below avoids that
# whole class of version-skew crash.
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# The imports below (RAG-related: embeddings, vector store, document loaders)
# pull in langchain_community, which has a history of version-skew crashes
# against langchain_core (e.g. ModuleNotFoundError: langchain_core.pydantic_v1).
# RAG is an OPTIONAL feature in this app (there's already a rule-based and
# LLM-only fallback), so we don't want a broken/incompatible optional
# dependency to prevent the whole Flask app from starting. Wrap each in its
# own try/except and fall back to None; the functions that use them already
# check for availability before use.
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except Exception as e:
    print(f"⚠️  HuggingFaceEmbeddings unavailable ({e}) — will try ONNX fallback")
    HuggingFaceEmbeddings = None

try:
    from langchain_community.vectorstores import Chroma
except Exception as e:
    print(f"⚠️  Chroma vector store unavailable ({e}) — RAG will be disabled")
    Chroma = None

try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
except Exception as e:
    print(f"⚠️  Document loaders unavailable ({e}) — RAG will be disabled")
    PyPDFLoader = None
    TextLoader = None

# Suppress warnings
warnings.filterwarnings("ignore")

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================
load_dotenv()

# ============================================================
# FLASK APP INITIALIZATION
# ============================================================
app = Flask(__name__)

# App configuration from .env or defaults
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fitgenie-default-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ============================================================
# DATABASE SETUP (SQLite with SQLAlchemy)
# ============================================================
db = SQLAlchemy(app)

# ============================================================
# FLASK-LOGIN SETUP
# ============================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated


# --- FIX #1 ------------------------------------------------------------
# By default, when @login_required rejects a request, Flask-Login
# REDIRECTS to /login and returns an HTML page (302 -> 200 HTML).
# Your JS chat widget does `fetch('/chat', ...).then(r => r.json())`.
# If the session cookie is missing/expired, the fetch silently receives
# an HTML login page instead of JSON, `r.json()` throws a SyntaxError,
# and your catch block reports it as a generic "network error" even
# though the server is perfectly reachable.
#
# This handler makes any request that "looks like" an API/AJAX call
# get a clean 401 JSON response instead of an HTML redirect, so the
# frontend can detect "you're logged out" instead of choking on HTML.
@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith(("/chat", "/save-profile", "/calculate-bmi",
                                 "/get-history", "/clear-history", "/upload-document")) \
            or request.is_json or request.accept_mimetypes.best == "application/json":
        return jsonify({"success": False, "message": "Session expired, please log in again."}), 401
    return redirect(url_for("login"))
# -------------------------------------------------------------------------


# ============================================================
# DATABASE MODELS
# ============================================================

class User(UserMixin, db.Model):
    """User model for authentication and profile linkage."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship("Profile", backref="user", uselist=False)
    chats = db.relationship("ChatHistory", backref="user", lazy=True)


class Profile(db.Model):
    """User fitness profile storing physical stats and goals."""
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Float, nullable=True)  # in cm
    weight = db.Column(db.Float, nullable=True)  # in kg
    gender = db.Column(db.String(20), nullable=True)
    goal = db.Column(db.String(100), nullable=True)
    fitness_level = db.Column(db.String(50), nullable=True)
    medical_condition = db.Column(db.Text, nullable=True)


class ChatHistory(db.Model):
    """Stores conversation history between user and AI assistant."""
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# CREATE ALL DATABASE TABLES
# ============================================================
with app.app_context():
    db.create_all()


# ============================================================
# FLASK-LOGIN USER LOADER
# ============================================================
@login_manager.user_loader
def load_user(user_id):
    """Required by Flask-Login to reload user from session."""
    return db.session.get(User, int(user_id))


# ============================================================
# LANGCHAIN / RAG SETUP
# ============================================================

def get_llm():
    """
    Initialize and return the Groq-hosted LLM via LangChain.
    Falls back to None if no valid API key is set (offline mode).

    Groq's free tier requires no billing setup, so this avoids the
    OpenAI "works once then 429 quota exceeded" problem entirely.
    Get a free key at https://console.groq.com/keys
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️  GROQ_API_KEY not found in environment")
        return None
    api_key = api_key.strip()
    if not api_key or "your-groq-api-key" in api_key:
        print("⚠️  GROQ_API_KEY is placeholder or empty")
        return None
    try:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=api_key
        )
    except Exception as e:
        print(f"❌ Failed to initialize Groq LLM: {e}")
        return None


def get_embeddings():
    """
    Initialize embeddings for document vectorization.

    Tries multiple backends in order:
    1. HuggingFace embeddings (requires sentence-transformers + torch)
    2. ChromaDB built-in ONNX embedding (lightweight, no extra deps)
    3. Returns None if neither is available (RAG disabled)
    """
    # Try HuggingFace embeddings first (best quality)
    if HuggingFaceEmbeddings is not None:
        try:
            import sentence_transformers
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
        except ImportError:
            print("⚠️  sentence-transformers not available, trying ONNX fallback...")
        except Exception as e:
            print(f"⚠️  HuggingFace embeddings failed: {e}")

    # Fallback: use ChromaDB's built-in ONNX embedding (no extra deps)
    try:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        onnx_ef = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
        # Wrap it as a LangChain-compatible Embeddings class
        from langchain_core.embeddings import Embeddings
        class ONNXEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return onnx_ef(texts)
            def embed_query(self, text):
                return onnx_ef([text])[0]
        print("✅ Using ChromaDB ONNX embeddings (lightweight)")
        return ONNXEmbeddings()
    except Exception as e:
        print(f"⚠️  ONNX embeddings also failed: {e}")

    return None


def load_and_split_documents():
    """
    Load PDF documents from the 'documents/' folder,
    split them into chunks for RAG processing.

    Chunk size: 500 characters with 100 character overlap
    to maintain context between chunks.
    """
    documents_dir = "documents"
    documents = []

    # Skip if directory doesn't exist
    if not os.path.exists(documents_dir):
        return []

    # Skip if loaders failed to import (version-skew issue in langchain_community)
    if PyPDFLoader is None or TextLoader is None:
        print("⚠️  Document loaders unavailable — skipping document loading")
        return []

    # Load all PDF and text files from the documents folder
    for filename in os.listdir(documents_dir):
        file_path = os.path.join(documents_dir, filename)

        try:
            # Load PDF files using PyPDFLoader
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

            # Load plain text files
            elif filename.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    if not documents:
        return []

    # Split documents into smaller chunks for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # Characters per chunk
        chunk_overlap=100,    # Overlap between chunks for context continuity
        separators=["\n\n", "\n", " ", ""]
    )

    return text_splitter.split_documents(documents)


def create_vector_store():
    """
    Create or load ChromaDB vector store from documents.

    The vector store persists on disk in the 'vectorstore/' directory
    so it doesn't need to be rebuilt every time the app starts.
    """
    import shutil
    persist_directory = "vectorstore"

    if Chroma is None:
        print("⚠️  Chroma unavailable — RAG disabled")
        return None

    embeddings = get_embeddings()

    if not embeddings:
        print("⚠️  No embeddings available — RAG disabled")
        return None

    # If vectorstore already exists, load it from disk
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        try:
            return Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"Error loading vectorstore: {e}, rebuilding...")
            shutil.rmtree(persist_directory, ignore_errors=True)

    # Otherwise, create it from documents
    chunks = load_and_split_documents()
    if not chunks:
        print("⚠️  No documents to index — RAG disabled")
        return None

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"✅ Vector store created with {len(chunks)} chunks from {len(os.listdir('documents'))} document(s)")
    return vector_store


RAG_PROMPT = PromptTemplate(
    template="""
    You are FitGenie AI, an expert fitness and nutrition assistant.

    INSTRUCTIONS:
    - Answer ONLY using the retrieved fitness information below.
    - If the retrieved information is not sufficient, use your general fitness knowledge.
    - Always give safe, science-based advice.
    - Keep responses concise and actionable (max 3-4 sentences).
    - Never recommend dangerous or extreme practices.
    - If the user mentions a medical condition, advise consulting a doctor.

    RECENT CONVERSATION:
    {chat_history}

    CONTEXT:
    {context}

    USER QUESTION:
    {question}

    YOUR RESPONSE:""",
    input_variables=["chat_history", "context", "question"]
)

LLM_ONLY_PROMPT = PromptTemplate(
    template="""
    You are FitGenie AI, an expert fitness and nutrition assistant.

    INSTRUCTIONS:
    - Use your general fitness knowledge to answer questions.
    - Always give safe, science-based advice.
    - Keep responses concise and actionable (max 3-4 sentences).
    - Never recommend dangerous or extreme practices.
    - If the user mentions a medical condition, advise consulting a doctor.
    - Remember what the user told you in previous messages.

    CONVERSATION HISTORY:
    {chat_history}

    USER QUESTION:
    {input}

    YOUR RESPONSE:""",
    input_variables=["chat_history", "input"]
)


# Global variable for the vector store (initialized on first use)
_vector_store = None
_vector_store_initialized = False


def get_vector_store():
    """Lazy singleton for the Chroma vector store (None if RAG is unavailable)."""
    global _vector_store, _vector_store_initialized
    if not _vector_store_initialized:
        _vector_store = create_vector_store()
        _vector_store_initialized = True
    return _vector_store


def generate_rag_answer(question, chat_history_text=""):
    """
    Tier 1: retrieve relevant document chunks and ask the LLM using them
    as context. Returns the answer string, or None if RAG isn't available
    or the call fails (caller should fall back to the next tier).

    This intentionally does NOT use ConversationalRetrievalChain — that
    chain (and LLMChain, ConversationBufferMemory) live in the legacy
    `langchain` umbrella package, which pulls in modules this app doesn't
    need and has repeatedly broken on langchain-core version mismatches.
    A direct retrieve -> format prompt -> llm.invoke() call needs only
    langchain_core + langchain_groq + (optionally) langchain_community's
    vector store, and is just as effective for this use case.
    """
    llm = get_llm()
    vector_store = get_vector_store()

    if not llm or not vector_store:
        return None

    docs = vector_store.similarity_search(question, k=3)
    if not docs:
        return None

    context = "\n\n".join(doc.page_content for doc in docs)
    prompt_text = RAG_PROMPT.format(
        chat_history=chat_history_text or "(no prior conversation)",
        context=context,
        question=question
    )
    response = llm.invoke(prompt_text)
    return (getattr(response, "content", None) or str(response)).strip()


def generate_llm_only_answer(question, chat_history_text=""):
    """
    Tier 2: plain LLM call with no document retrieval, used when RAG is
    unavailable or returned nothing. See generate_rag_answer() for why
    this avoids LLMChain/ConversationBufferMemory.
    """
    llm = get_llm()
    if not llm:
        return None

    prompt_text = LLM_ONLY_PROMPT.format(
        chat_history=chat_history_text or "(no prior conversation)",
        input=question
    )
    response = llm.invoke(prompt_text)
    return (getattr(response, "content", None) or str(response)).strip()


def get_fallback_response(question):
    """
    Generate a response when LLM/vector store is unavailable.
    Uses simple rule-based logic for common fitness questions.
    """
    question_lower = question.lower()

    # BMI-related questions
    if "bmi" in question_lower:
        return (
            "BMI (Body Mass Index) is a measure of body fat based on height and weight. "
            "Formula: BMI = weight(kg) / height(m)². "
            "Categories: Underweight < 18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese ≥ 30. "
            "Note: BMI is a screening tool, not a diagnostic test."
        )

    # Workout-related questions
    if any(word in question_lower for word in ["workout", "exercise", "gym", "training"]):
        return (
            "A balanced fitness routine includes: "
            "1) Strength training (3-4 days/week), "
            "2) Cardio (150 min/week moderate or 75 min vigorous), "
            "3) Flexibility work (daily stretching), "
            "4) Rest days for recovery. "
            "Always warm up before and cool down after exercise."
        )

    # Nutrition-related questions
    if any(word in question_lower for word in ["diet", "nutrition", "food", "eat", "meal", "protein"]):
        return (
            "For balanced nutrition: "
            "Eat lean proteins (chicken, fish, tofu), complex carbs (whole grains, vegetables), "
            "healthy fats (avocado, nuts, olive oil), and stay hydrated (8+ glasses water/day). "
            "Aim for a calorie deficit of 300-500 calories/day for weight loss, "
            "or a surplus for muscle gain."
        )

    # Weight loss questions
    if any(word in question_lower for word in ["lose weight", "fat", "belly fat", "slim"]):
        return (
            "Sustainable weight loss requires: "
            "1) Calorie deficit (300-500 cal/day below maintenance), "
            "2) Regular exercise (cardio + strength training), "
            "3) Adequate sleep (7-9 hours), "
            "4) Stress management. "
            "Spot reduction (losing belly fat specifically) is not possible - "
            "overall body fat reduction is the key."
        )

    # General fallback
    return (
        "I'm FitGenie AI! I can help with: "
        "🏋️ Workout plans, 🥗 Nutrition advice, 📊 BMI analysis, "
        "💪 Fitness tips, and more. "
        "Please ask me a specific fitness or health question!"
    )


# ============================================================
# FLASK ROUTES - AUTHENTICATION
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User Registration Route
    GET: Display registration form
    POST: Process registration with validation
    """
    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # --- Validation ---

        # Check if all fields are filled
        if not all([name, email, password, confirm_password]):
            flash("All fields are required!", "error")
            return render_template("register.html")

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please login.", "error")
            return render_template("register.html")

        # Check password length (minimum 6 characters)
        if len(password) < 6:
            flash("Password must be at least 6 characters long!", "error")
            return render_template("register.html")

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html")

        # --- Create new user ---
        # Hash password using Werkzeug for security
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # Create empty profile for the new user
            profile = Profile(user_id=new_user.id)
            db.session.add(profile)
            db.session.commit()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    User Login Route
    GET: Display login form
    POST: Authenticate user credentials
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = True if request.form.get("remember") else False

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Verify user exists and password is correct
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")

            # Store user info in session for easy access
            session["user_name"] = user.name
            session["user_id"] = user.id

            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Logout the current user and clear session."""
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ============================================================
# FLASK ROUTES - DASHBOARD & PROFILE
# ============================================================

@app.route("/")
@login_required
def dashboard():
    """
    Main Dashboard Route
    Displays user info, BMI, fitness stats, and recent chat history.
    """
    # Get user profile
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    # Calculate BMI if height and weight are available
    bmi = None
    bmi_category = None
    if profile and profile.height and profile.weight and profile.height > 0:
        height_m = profile.height / 100  # Convert cm to meters
        bmi = round(profile.weight / (height_m ** 2), 1)

        # Determine BMI category
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 25:
            bmi_category = "Normal"
        elif 25 <= bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

    # Get recent chat history (last 5 conversations)
    recent_chats = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        profile=profile,
        bmi=bmi,
        bmi_category=bmi_category,
        recent_chats=recent_chats
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    User Profile Route
    GET: Display profile form with current data
    POST: Save/update user fitness profile
    """
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        # Update profile fields from form data
        profile.age = request.form.get("age", type=int)
        profile.height = request.form.get("height", type=float)
        profile.weight = request.form.get("weight", type=float)
        profile.gender = request.form.get("gender")
        profile.goal = request.form.get("goal")
        profile.fitness_level = request.form.get("fitness_level")
        profile.medical_condition = request.form.get("medical_condition")

        try:
            db.session.commit()
            flash("Profile saved successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving profile: {str(e)}", "error")

        return redirect(url_for("dashboard"))

    return render_template("profile.html", profile=profile)


@app.route("/save-profile", methods=["POST"])
@login_required
def save_profile():
    """
    API endpoint to save profile via AJAX.
    Used by the JavaScript frontend for seamless updates.
    """
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        return jsonify({"success": False, "message": "Profile not found"}), 404

    # FIX #2: silent=True so a missing/incorrect Content-Type header
    # (very common from plain `fetch(url, {method:'POST', body: JSON.stringify(...)})`
    # calls that forget `headers: {'Content-Type': 'application/json'}`)
    # returns None instead of raising a 400/415 error that produced an
    # HTML error page the frontend couldn't parse as JSON.
    data = request.get_json(silent=True) or {}
    if data:
        profile.age = data.get("age", profile.age)
        profile.height = data.get("height", profile.height)
        profile.weight = data.get("weight", profile.weight)
        profile.gender = data.get("gender", profile.gender)
        profile.goal = data.get("goal", profile.goal)
        profile.fitness_level = data.get("fitness_level", profile.fitness_level)
        profile.medical_condition = data.get("medical_condition", profile.medical_condition)

        try:
            db.session.commit()
            return jsonify({"success": True, "message": "Profile saved!"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500

    return jsonify({"success": False, "message": "No data provided"}), 400


# ============================================================
# FLASK ROUTES - BMI CALCULATOR
# ============================================================

@app.route("/calculate-bmi", methods=["POST"])
@login_required
def calculate_bmi():
    """
    BMI Calculator API Endpoint
    Accepts weight (kg) and height (cm), returns BMI and health advice.
    """
    data = request.get_json(silent=True) or {}  # FIX #2 (see save_profile)

    weight = data.get("weight")
    height = data.get("height")

    if not weight or not height:
        return jsonify({"success": False, "message": "Weight and height required"}), 400

    try:
        weight = float(weight)
        height = float(height)

        if weight <= 0 or height <= 0:
            raise ValueError("Values must be positive")

        # BMI calculation: weight(kg) / height(m)²
        height_m = height / 100
        bmi = round(weight / (height_m ** 2), 1)

        # Determine category and advice
        if bmi < 18.5:
            category = "Underweight"
            advice = (
                "You are underweight. Consider a nutrient-dense diet with healthy "
                "calorie surplus. Focus on strength training to build muscle mass. "
                "Consult a dietitian for a personalized plan."
            )
        elif 18.5 <= bmi < 25:
            category = "Normal"
            advice = (
                "You have a healthy BMI. Maintain your current lifestyle with "
                "balanced nutrition and regular exercise. Focus on strength training "
                "and cardiovascular fitness."
            )
        elif 25 <= bmi < 30:
            category = "Overweight"
            advice = (
                "You are in the overweight range. Consider a moderate calorie deficit, "
                "increased physical activity (cardio + weights), and portion control. "
                "Small consistent changes lead to sustainable results."
            )
        else:
            category = "Obese"
            advice = (
                "You are in the obese range. We recommend consulting a healthcare "
                "provider before starting any fitness program. Focus on low-impact "
                "exercises, balanced nutrition, and gradual lifestyle changes."
            )

        return jsonify({
            "success": True,
            "bmi": bmi,
            "category": category,
            "advice": advice
        })

    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid input values"}), 400


# ============================================================
# FLASK ROUTES - AI CHAT
# ============================================================

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    """
    AI Chat API Endpoint
    Accepts user question, generates response using RAG pipeline or fallback.
    Saves conversation to chat history.
    """
    # FIX #2: silent=True avoids a raw 400/415 (HTML) response when the
    # request body is missing or the Content-Type header isn't set to
    # application/json — this alone was very likely the "network error"
    # your JS was reporting, since `res.json()` on an HTML body throws.
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"success": False, "message": "Question is required"}), 400

    # FIX #3: wrap the rest of the handler so ANY unexpected exception
    # (DB hiccup, LangChain internals, etc.) still comes back as JSON
    # instead of Flask's HTML debug traceback page — which is exactly
    # the kind of response that breaks `fetch().then(r => r.json())`
    # and shows up in the UI as a generic "network error".
    try:
        # Build context from user profile for personalized responses
        profile = Profile.query.filter_by(user_id=current_user.id).first()
        user_context = ""
        if profile:
            details = []
            if profile.age:
                details.append(f"Age: {profile.age}")
            if profile.gender:
                details.append(f"Gender: {profile.gender}")
            if profile.goal:
                details.append(f"Goal: {profile.goal}")
            if profile.fitness_level:
                details.append(f"Fitness Level: {profile.fitness_level}")
            if profile.medical_condition:
                details.append(f"Medical Condition: {profile.medical_condition}")
            if profile.weight and profile.height:
                details.append(f"BMI: {round(profile.weight / ((profile.height / 100) ** 2), 1)}")
            if details:
                user_context = f"User Info: {' | '.join(details)}"

        # Build contextual question with user profile info
        contextual_question = f"{user_context}\nQuestion: {question}" if user_context else question

        # Pull recent conversation history from the DB to give the LLM
        # continuity across turns (replaces the old in-memory
        # ConversationBufferMemory, which was lost on every restart anyway).
        recent = ChatHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(ChatHistory.timestamp.desc()).limit(4).all()
        chat_history_text = "\n".join(
            f"User: {c.question}\nFitGenie AI: {c.answer}" for c in reversed(recent)
        )

        # Try 3 tiers: RAG → LLM-only → rule-based fallback
        answer = None

        # Tier 1: RAG pipeline (LLM + vector store)
        try:
            answer = generate_rag_answer(contextual_question, chat_history_text)
            if answer:
                print(f"✅ RAG response for: {question[:50]}...")
        except Exception as e:
            print(f"⚠️  RAG failed: {e}")

        # Tier 2: LLM-only (no vector store, still uses Groq)
        if not answer:
            try:
                answer = generate_llm_only_answer(contextual_question, chat_history_text)
                if answer:
                    print(f"✅ LLM-only response for: {question[:50]}...")
            except Exception as e:
                print(f"⚠️  LLM-only failed: {e}")

        # Tier 3: Rule-based fallback (no API key at all)
        if not answer:
            answer = get_fallback_response(question)
            print(f"⚠️  Fallback response for: {question[:50]}...")

        # Save chat history to database
        try:
            chat_entry = ChatHistory(
                user_id=current_user.id,
                question=question,
                answer=answer
            )
            db.session.add(chat_entry)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({
            "success": True,
            "question": question,
            "answer": answer
        })

    except Exception as e:
        print(f"❌ /chat crashed unexpectedly: {e}")
        return jsonify({
            "success": False,
            "message": "Something went wrong generating a response. Please try again."
        }), 500


@app.route("/get-history", methods=["GET"])
@login_required
def get_history():
    """
    Retrieve chat history for the current user.
    Returns last 50 conversations in reverse chronological order.
    """
    chats = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(ChatHistory.timestamp.desc()).limit(50).all()

    history = [
        {
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "timestamp": chat.timestamp.strftime("%Y-%m-%d %H:%M")
        }
        for chat in chats
    ]

    return jsonify({"success": True, "history": history})


@app.route("/clear-history", methods=["POST"])
@login_required
def clear_history():
    """Delete all chat history for the current user."""
    try:
        ChatHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"success": True, "message": "Chat history cleared!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================================
# FLASK ROUTES - DOCUMENT MANAGEMENT
# ============================================================

@app.route("/upload-document", methods=["POST"])
@login_required
def upload_document():
    """
    Upload fitness documents for RAG processing.
    Accepted formats: PDF (.pdf) and Text (.txt)
    After upload, the vector store needs to be rebuilt.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # Validate file extension
    allowed_extensions = {".pdf", ".txt"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        return jsonify({
            "success": False,
            "message": "Only PDF and TXT files are supported"
        }), 400

    # Ensure documents directory exists
    os.makedirs("documents", exist_ok=True)

    # Save file
    file_path = os.path.join("documents", file.filename)
    file.save(file_path)

    # Reset the vector store singleton so it rebuilds with the new document
    global _vector_store, _vector_store_initialized
    _vector_store = None
    _vector_store_initialized = False

    return jsonify({
        "success": True,
        "message": f"Document '{file.filename}' uploaded successfully!"
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with a JSON response for API calls."""
    if request.path.startswith("/api") or request.is_json:
        return jsonify({"success": False, "message": "Resource not found"}), 404
    flash("Page not found!", "error")
    return redirect(url_for("dashboard"))


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors gracefully."""
    if request.is_json:
        return jsonify({"success": False, "message": "Internal server error"}), 500
    flash("Something went wrong. Please try again.", "error")
    return redirect(url_for("dashboard"))


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    """
    Run the Flask development server.

    For production, use a production WSGI server like Gunicorn or Waitress:
        pip install waitress
        waitress-serve --port=5000 app:app
    """
    # Ensure required directories exist
    os.makedirs("documents", exist_ok=True)
    os.makedirs("vectorstore", exist_ok=True)

    # --- Startup Diagnostics ---
    print("=" * 60)
    print("  FitGenie AI - Intelligent Fitness Assistant")
    print("  Running on http://127.0.0.1:5000")
    print("=" * 60)
    print()

    # Check Groq API key
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and api_key.strip() and "your-groq-api-key" not in api_key:
        print("  ✅ Groq API key found")
    else:
        print("  ⚠️  No valid Groq API key — using rule-based fallback")
        print("     Set GROQ_API_KEY in .env for AI-powered responses")
        print("     Get a free key at https://console.groq.com/keys")

    # Check embeddings availability
    try:
        import sentence_transformers
        print("  ✅ sentence-transformers available (GPU-quality embeddings)")
    except ImportError:
        try:
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
            print("  ✅ ChromaDB ONNX embeddings available (lightweight fallback)")
        except ImportError:
            print("  ⚠️  No embedding backend — RAG will be unavailable")

    # Check documents folder
    doc_count = len([f for f in os.listdir("documents") if f.endswith((".pdf", ".txt"))]) if os.path.exists("documents") else 0
    if doc_count > 0:
        print(f"  ✅ {doc_count} document(s) found for RAG")
    else:
        print("  ⚠️  No documents found — RAG will be unavailable")
        print("     Place .pdf or .txt files in the 'documents/' folder")

    # Check vectorstore
    if os.path.exists("vectorstore") and os.listdir("vectorstore"):
        print("  ✅ Vector store exists")
    else:
        print("  ℹ️  Vector store will be created on first chat")

    print()
    print("  📋 Quick start:")
    print("  1. Register at http://127.0.0.1:5000/register")
    print("  2. Update your fitness profile")
    print("  3. Start chatting with FitGenie AI!")
    print()

    app.run(debug=True, host="0.0.0.0", port=5000)