"""
FitGenie AI - AI-Powered Fitness Assistant
Flask + LangChain + RAG + ChromaDB + OpenAI
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
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

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
    Initialize and return the OpenAI GPT model via LangChain.
    Falls back to a mock/offline mode if no API key is set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openai-api-key-here":
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=api_key
        )
    # Return None if no valid API key (offline mode)
    return None


def get_embeddings():
    """
    Initialize HuggingFace embeddings for document vectorization.
    Uses all-MiniLM-L6-v2 model for efficient sentence embeddings.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


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
    embeddings = get_embeddings()
    
    # If vectorstore already exists, load it from disk
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        try:
            return Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
        except Exception as e:
            print(f"Error loading vectorstore: {e}, rebuilding...")
            # If loading fails, remove and rebuild
            shutil.rmtree(persist_directory, ignore_errors=True)
    
    # Otherwise, create it from documents
    chunks = load_and_split_documents()
    if not chunks:
        return None
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vector_store


def create_retrieval_qa():
    """
    Build the complete RAG chain with conversation memory using LangChain.
    
    Components:
    1. Vector store retriever (finds relevant document chunks)
    2. Custom prompt template for fitness-specific responses
    3. Conversation buffer memory for context retention
    4. OpenAI LLM for generating final answers
    """
    llm = get_llm()
    vector_store = create_vector_store()
    
    # If no LLM or vector store, return None (fallback mode)
    if not llm or not vector_store:
        return None
    
    # Custom prompt template tailored for fitness advice
    # Note: ConversationalRetrievalChain uses "context" and "question" as input variables
    prompt_template = """
    You are FitGenie AI, an expert fitness and nutrition assistant.

    INSTRUCTIONS:
    - Answer ONLY using the retrieved fitness information below.
    - If the retrieved information is not sufficient, use your general fitness knowledge.
    - Always give safe, science-based advice.
    - Keep responses concise and actionable (max 3-4 sentences).
    - Never recommend dangerous or extreme practices.
    - If the user mentions a medical condition, advise consulting a doctor.

    CONTEXT:
    {context}

    USER QUESTION:
    {question}

    YOUR RESPONSE:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Conversation memory to remember previous interactions
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True
    )
    
    # Build the Conversational Retrieval Chain with memory
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(
            search_kwargs={"k": 3}  # Retrieve top 3 relevant chunks
        ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=False,
        verbose=False
    )
    
    return qa_chain


# Global variable for the QA chain (initialized on first use)
qa_chain = None


def get_qa_chain():
    """Lazy initialization of the QA chain (singleton pattern)."""
    global qa_chain
    if qa_chain is None:
        qa_chain = create_retrieval_qa()
    return qa_chain


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

    # Update fields from JSON request
    data = request.get_json()
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
    data = request.get_json()

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
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"success": False, "message": "Question is required"}), 400

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

    # Try to use RAG pipeline, fall back to rule-based responses
    try:
        chain = get_qa_chain()
        if chain:
            # Include user context for personalization
            contextual_question = f"{user_context}\nQuestion: {question}" if user_context else question
            # ConversationalRetrievalChain uses "question" as the input key
            result = chain.invoke({"question": contextual_question})
            answer = result.get("answer", "").strip()
        else:
            # Fallback mode (no API key or vector store)
            answer = get_fallback_response(question)
    except Exception as e:
        # If RAG fails, use fallback
        print(f"RAG Error: {e}")
        answer = get_fallback_response(question)

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

    # Reset QA chain so it rebuilds with the new document
    global qa_chain
    qa_chain = None

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

    print("=" * 60)
    print("  FitGenie AI - Intelligent Fitness Assistant")
    print("  Running on http://127.0.0.1:5000")
    print("=" * 60)
    print()
    print("  📋 Make sure to:")
    print("  1. Add your OPENAI_API_KEY to .env file")
    print("  2. Place PDF files in the 'documents/' folder")
    print("  3. Register a new account at /register")
    print()

    app.run(debug=True, host="0.0.0.0", port=5000)
