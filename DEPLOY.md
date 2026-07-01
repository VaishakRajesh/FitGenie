# DEPLOY.md - Free Deployment Guide for FitGenie AI

A comprehensive guide to deploying the FitGenie AI Flask application on free-tier hosting platforms.

---

## Table of Contents

1. [PythonAnywhere (easiest, free tier)](#1-pythonanywhere-free---best-for-beginners)
2. [Render (most modern, free tier)](#2-render-free---most-modern)
3. [Railway (simple, free tier)](#3-railway-simple-free-tier)
4. [Koyeb (alternative free tier)](#4-koyeb-alternative-free-tier)
5. [Oracle Cloud Always Free (most powerful)](#5-oracle-cloud-always-free-tier-most-powerful)
6. [Important Notes](#important-notes)

---

## Prerequisites

Before deploying, make sure you have:

- A GitHub account with your FitGenie repository pushed
- An OpenAI API key (optional — app works in fallback mode without it)
- The `requirements.txt` file already in your repo (it's already done)

---

## 1. PythonAnywhere (FREE - Best for Beginners)

PythonAnywhere gives you a persistent filesystem, a Bash console, and one web app on the free tier. Perfect for Flask.

### Step-by-Step

#### 1. Create an account

1. Go to https://www.pythonanywhere.com
2. Click **Pricing & signup** → **Create a Beginner account** (free)
3. Choose your username — this will be part of your URL: `yourusername.pythonanywhere.com`
4. Check your email and confirm

#### 2. Upload your code

**Option A — Clone from GitHub (recommended):**

1. From your dashboard, click **Consoles** → **Bash**
2. Run:
```bash
git clone https://github.com/YOUR_USERNAME/fitgenie-ai.git fitgenie
cd fitgenie
```

**Option B — Upload files manually:**

1. Click **Files** tab
2. Navigate to `/home/yourusername/`
3. Click **Upload a file** and upload each file, or use the **Upload multiple files** button
4. Create subdirectories: `documents/`, `vectorstore/`, `instance/`, `static/`, `templates/`

#### 3. Create a virtual environment

In the Bash console:
```bash
cd ~/fitgenie
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **Important:** Free tier only supports Python 3.10–3.12. Python 3.11 is recommended.

#### 4. Configure the Web App

1. Click the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** (not "Flask" — we'll configure it ourselves)
4. Select **Python 3.11**

#### 5. Edit the WSGI file

1. In the **Web** tab, under **Code**, click the link to the WSGI configuration file (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
2. Replace everything with:

```python
import sys
import os

# Add your project directory to the Python path
path = '/home/yourusername/fitgenie'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key-here'
os.environ['SECRET_KEY'] = 'your-strong-secret-key-here'
os.environ['DATABASE_URL'] = 'sqlite://///home/yourusername/fitgenie/instance/database.db'

# Import the Flask app
from app import app as application
```

3. Replace `yourusername` with your actual PythonAnywhere username
4. Click **Save**

#### 6. Set up environment variables

In the **Web** tab, scroll to **Environment variables** and click **Add environment variable**. Add these:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | `sk-...` your OpenAI key |
| `SECRET_KEY` | A random 64-character hex string |
| `DATABASE_URL` | `sqlite://///home/yourusername/fitgenie/instance/database.db` |

#### 7. Configure static files

In the **Web** tab, under **Static files**:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/fitgenie/static` |

#### 8. Handle SQLite database

The SQLite database will be stored at `/home/yourusername/fitgenie/instance/database.db`. This persists on PythonAnywhere — it won't be wiped on restarts.

To initialize the database on first run:

1. Open the Bash console
2. Run:
```bash
cd ~/fitgenie
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### 9. Handle ChromaDB vectorstore and documents

The vectorstore lives at `/home/yourusername/fitgenie/vectorstore/` and documents at `/home/yourusername/fitgenie/documents/`. Both persist permanently on PythonAnywhere.

1. Upload your PDF documents to `/home/yourusername/fitgenie/documents/`
2. The vectorstore will be created automatically on first request

#### 10. Reload

Click the green **Reload** button in the **Web** tab.

### Screenshot Descriptions

| Step | What you'll see |
|------|----------------|
| Creating account | A purple/pink signup form with username, email, and password fields |
| Dashboard | A top nav with Consoles, Files, Web, Tasks tabs; a resource usage meter on the right |
| Web tab config | "Code", "Security", "Static files", "Environment variables" sections with edit links |
| WSGI editor | A text editor with syntax-highlighted Python code; Save button at bottom |
| Environment variables | A table with Key/Value inputs and an "Add variable" button |

### Troubleshooting

- **500 Internal Server Error:** Check the **Error log** link in the **Web** tab under **Logs**
- **ModuleNotFoundError:** Make sure you activated the virtualenv and ran `pip install -r requirements.txt`
- **Static files not loading:** Verify the static files path in the **Web** tab is `/home/yourusername/fitgenie/static`
- **Database errors:** Run `python -c "from app import app, db; app.app_context().push(); db.create_all()"` manually from the Bash console
- **ChromaDB errors:** Clear the vectorstore directory and let it rebuild: `rm -rf ~/fitgenie/vectorstore/*`

---

## 2. Render (FREE - Most Modern)

Render offers a free tier with 512 MB RAM, persistent disk (1 GB), and auto-deploy from GitHub.

### Step-by-Step

#### 1. Create an account

1. Go to https://dashboard.render.com
2. Sign up with GitHub (recommended) or email
3. Verify your email address

#### 2. Add a Persistent Disk (Render Disks)

Render free web services include **1 GB of persistent disk storage**. You must mount it manually.

#### 3. Create a Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub account if not already done
3. Select your FitGenie repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `fitgenie-ai` |
| **Region** | Choose the closest to you |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan Type** | **Free** |

> **Important:** For the free plan, the service spins down after 15 minutes of inactivity and spins up on the next request (cold start). This takes 30–60 seconds.

#### 4. Add environment variables

Scroll to **Environment Variables** and add:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-...` |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | `sqlite:////var/data/instance/database.db` |
| `PYTHON_VERSION` | `3.11.7` |

#### 5. Mount persistent disk for SQLite, vectorstore, and documents

1. Scroll to **Disks** in the web service settings
2. Click **Add Disk**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `fitgenie-data` |
| **Mount Path** | `/var/data` |
| **Size** | `1 GB` (free) |

4. This path `/var/data` will be used for all persistent data.

#### 6. Create required subdirectories

Add a `render-init.sh` script to your repo to initialize directories on deploy:

```bash
#!/bin/bash
# render-init.sh - Run before starting the app

# Create persistent directories
mkdir -p /var/data/instance
mkdir -p /var/data/documents
mkdir -p /var/data/vectorstore

# Initialize the database
python -c "
from app import app, db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/data/instance/database.db'
app.app_context().push()
db.create_all()
print('Database initialized at /var/data/instance/database.db')
"
```

Update the **Start Command** in Render to:
```
chmod +x render-init.sh && ./render-init.sh && gunicorn app:app
```

#### 7. Update the app to use the mounted disk path

You may need to modify `app.py` to check for the `/var/data` path. Add this near the top of `app.py`:

```python
# Use Render persistent disk if available
if os.path.exists("/var/data"):
    DATABASE_PATH = "/var/data/instance/database.db"
    DOCUMENTS_DIR = "/var/data/documents"
    VECTORSTORE_DIR = "/var/data/vectorstore"
else:
    DATABASE_PATH = "instance/database.db"
    DOCUMENTS_DIR = "documents"
    VECTORSTORE_DIR = "vectorstore"
```

Then replace hardcoded `"documents"` and `"vectorstore"` strings with the variables.

#### 8. Deploy

1. Click **Create Web Service**
2. Render will build and deploy automatically
3. Once done, your app is at: `https://fitgenie-ai.onrender.com`

### Screenshot Descriptions

| Step | What you'll see |
|------|----------------|
| New Web Service form | Repository selection list; then a configuration form with name, region, branch, runtime, build/start commands, plan selector |
| Environment Variables | A table with Key/Value fields and an "Add Environment Variable" button |
| Disks section | A "Add Disk" button; after adding shows mount path and size |
| Build log | Real-time terminal output showing pip install steps |
| Live service | A green "Live" badge; service URL; CPU/memory graphs |

### Troubleshooting

- **Cold start delay:** Normal for free tier (30–60s on first request after idle)
- **Disk not mounted:** Check the **Disks** section in your web service settings — ensure it's attached
- **Database not persisting:** Verify `DATABASE_URL` points to `/var/data/instance/database.db`
- **Vectorstore rebuilt every deploy:** Make sure it's writing to `/var/data/vectorstore`
- **Check logs:** Render dashboard → your service → **Logs** tab

### Configuration Files

Create a `Procfile` in the root of your project:

```procfile
web: gunicorn app:app
```

Create a `runtime.txt`:

```
python-3.11.7
```

---

## 3. Railway (Simple, Free Tier)

Railway offers a free tier with $5 of credits monthly (enough for a small Flask app) and a simple GitHub-connected workflow.

### Step-by-Step

#### 1. Create an account

1. Go to https://railway.app
2. Click **Login with GitHub**
3. Authorize Railway

#### 2. Create a project

1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Select your FitGenie repository
4. Railway auto-detects Python and uses Nixpacks to build

#### 3. Configure the service

Railway automatically detects Python projects. It will use `requirements.txt` and `nixpacks.toml` if present.

Create a `nixpacks.toml` file in your repository root:

```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn app:app"
```

#### 4. Add environment variables

In the Railway dashboard, navigate to your service → **Variables** tab and add:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-...` |
| `SECRET_KEY` | Your secret key |
| `DATABASE_URL` | `sqlite:////app/instance/database.db` |

> Railway's filesystem is **ephemeral** — files are reset on each deploy. SQLite and ChromaDB data will be lost on redeploy. For persistence, use Railway's **Volume** feature or switch to an external PostgreSQL/MySQL database.

#### 5. Add a persistent volume (for SQLite & ChromaDB)

1. In your service dashboard, click **Settings** → **Volumes**
2. Click **Add Volume**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `fitgenie-data` |
| **Mount Path** | `/app/data` |
| **Size** | `1 GB` |

4. Update `DATABASE_URL` to: `sqlite:////app/data/instance/database.db`
5. Update your `app.py` to use `/app/data/documents` and `/app/data/vectorstore`

#### 6. Deploy

1. Push to GitHub — Railway auto-deploys
2. Your app URL is shown at the top of the service dashboard (e.g., `https://fitgenie-ai.up.railway.app`)

### Screenshot Descriptions

| Step | What you'll see |
|------|----------------|
| Dashboard | A card-based layout showing your projects; "+ New Project" button |
| Service view | Build logs in real-time; Variables tab; Settings tab with Volumes section |
| Variables | A key-value editor with "New Variable" button and reveal/hide toggle |
| Volumes | Volume name, mount path, size fields; "Add Volume" confirmation |

### Troubleshooting

- **Nixpacks not using Python 3.11:** Add `nixpacks.toml` as shown above
- **Data lost after deploy:** Add a persistent volume — Railway doesn't keep filesystem changes
- **Build takes too long:** Free tier has limited build minutes; be efficient with requirements
- **Port binding issues:** Railway sets `$PORT` env var automatically; Flask app should use `port=os.getenv('PORT', 5000)`
- **See logs:** Service dashboard → **Deployments** → click a deployment → **View Logs**

---

## 4. Koyeb (Alternative Free Tier)

Koyeb offers a free tier with 1 GB RAM, a persistent filesystem, and global edge network.

### Step-by-Step

#### 1. Create an account

1. Go to https://app.koyeb.com
2. Sign up with GitHub
3. Verify your email

#### 2. Create a Web Service

1. Click **Create App**
2. Select **GitHub** as deployment method
3. Authorize Koyeb and select your repository
4. Click **Next**

#### 3. Configure build and run

| Setting | Value |
|---------|-------|
| **Builder** | `Dockerfile` or `Buildpack` |
| **Build Command** | `pip install -r requirements.txt` |
| **Run Command** | `gunicorn app:app` |

> If using Buildpack, Koyeb detects Python automatically.

#### 4. Add environment variables

Add these in the app settings:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-...` |
| `SECRET_KEY` | Your secret key |
| `DATABASE_URL` | `sqlite:////data/instance/database.db` |

#### 5. Add persistent storage

Koyeb offers `/data` as a persistent directory:

1. In the **App Settings** → **Volumes** section
2. The `/data` path persists across redeploys automatically on paid plans; on free tier, check if persistent storage is included (currently available in the free trial).

Alternatively, create a `Dockerfile` for more control:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create persistent directories
RUN mkdir -p /data/instance /data/documents /data/vectorstore

# Symlink for backward compatibility
RUN ln -sf /data/instance ./instance
RUN ln -sf /data/documents ./documents
RUN ln -sf /data/vectorstore ./vectorstore

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
```

#### 6. Deploy

1. Click **Create App**
2. Koyeb will build and deploy
3. Your URL: `https://fitgenie-ai-<name>.koyeb.app`

### Troubleshooting

- **Buildpack detection fails:** Use the Dockerfile approach instead
- **Persistent storage:** Check Koyeb free tier docs for current /data persistence policy
- **Memory limits:** Free tier has 1 GB RAM — should be sufficient for Flask + ChromaDB

---

## 5. Oracle Cloud Always Free Tier (Most Powerful)

Oracle Cloud's Always Free tier includes an ARM Ampere VM with 4 OCPUs and 24 GB RAM — the most powerful free option. You get a full Linux server.

### Step-by-Step

#### 1. Create an Oracle Cloud account

1. Go to https://cloud.oracle.com
2. Click **View Plans** → **Start for free** → **Create a free account**
3. Fill in your details (requires a credit card for identity verification — you won't be charged)
4. Verify email and phone

#### 2. Create a VM instance

1. Log in to the Oracle Cloud console
2. Go to **Compute** → **Instances**
3. Click **Create Instance**
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `fitgenie-server` |
| **Image** | Canonical Ubuntu 22.04 (or 24.04) |
| **Shape** | **VM.Standard.A1.Flex** (ARM, Ampere) |
| **OCPUs** | 4 |
| **Memory** | 24 GB |
| **Boot volume** | 200 GB (always free) |

5. Under **Add SSH keys**, paste your public key or generate a new key pair
6. Click **Create**

#### 3. Connect to the VM

Using SSH (from Git Bash, WSL, or PuTTY on Windows):

```bash
ssh -i ~/.ssh/your-key ubuntu@<PUBLIC_IP>
```

> Find the public IP in the instance details page in the Oracle Cloud console.

#### 4. Install dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx
```

#### 5. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/fitgenie-ai.git fitgenie
cd fitgenie
```

#### 6. Set up virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

#### 7. Create a `.env` file

```bash
nano .env
```

Contents:

```
OPENAI_API_KEY=sk-...
SECRET_KEY=your-64-char-hex-secret
DATABASE_URL=sqlite:///instance/database.db
```

#### 8. Set up systemd service (auto-start on boot)

```bash
sudo nano /etc/systemd/system/fitgenie.service
```

Contents:

```ini
[Unit]
Description=FitGenie AI Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/fitgenie
Environment="PATH=/home/ubuntu/fitgenie/venv/bin"
ExecStart=/home/ubuntu/fitgenie/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable fitgenie
sudo systemctl start fitgenie
```

Check status:
```bash
sudo systemctl status fitgenie
```

#### 9. Set up Nginx as reverse proxy

```bash
sudo nano /etc/nginx/sites-available/fitgenie
```

Contents:

```nginx
server {
    listen 80;
    server_name your-domain.com YOUR_VM_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /home/ubuntu/fitgenie/static/;
        expires 30d;
    }

    client_max_body_size 50M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/fitgenie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 10. Configure firewall

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

#### 11. (Optional) Set up HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

#### 12. Initialize the database

```bash
cd ~/fitgenie
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### 13. Upload documents

```bash
# Upload via SCP from your local machine:
scp -i ~/.ssh/your-key your-document.pdf ubuntu@<PUBLIC_IP>:~/fitgenie/documents/

# Or on the server directly:
# Place PDF files in ~/fitgenie/documents/
```

### Screenshot Descriptions

| Step | What you'll see |
|------|----------------|
| VM creation | A multi-tab form: Name/OS/Shape/Networking/SSH keys; Shape selection showing Ampere A1 with 4 OCPUs and 24 GB RAM labeled "Always Free" |
| Instance list | A table with instance name, status (running), public IP, shape |
| Security list | A firewall rules editor for ingress (port 80, 443, 22) and egress |
| SSH terminal | A command-line prompt (`ubuntu@fitgenie-server:~$`) after successful connection |

### Troubleshooting

- **SSH connection refused:** Ensure port 22 is open in the VCN security list (Virtual Cloud Network → Security Lists → Add Ingress Rule: Source 0.0.0.0/0, Destination port 22, TCP)
- **Nginx 502 Bad Gateway:** Gunicorn might not be running — check `sudo systemctl status fitgenie`
- **Static files not loading:** Verify the Nginx `alias` path is correct
- **Out of memory:** The Free Tier has 24 GB — you won't hit limits with Flask
- **Boot volume full:** 200 GB is plenty, but run `df -h` to check

---

## Important Notes

### OpenAI API Key

- The app requires `OPENAI_API_KEY` for full AI-powered responses using GPT
- **Without it**, the app runs in **fallback rule-based mode** — it returns predefined fitness advice but won't use the RAG pipeline or answer novel questions
- Set it as an environment variable on every platform
- Never commit your real API key to GitHub — use `.env` locally and environment variables in production
- OpenAI API key format: `sk-proj-...`

### SQLite Database

- By default, the app uses SQLite at `instance/database.db`
- SQLite is **file-based** — it works on platforms with persistent storage (PythonAnywhere, Oracle Cloud, Render with Disk)
- On platforms with ephemeral filesystems (Railway without Volume, Heroku free tier), data is **lost on restart**
- For production: switch to **managed PostgreSQL** (free tiers available on Render, Railway, Supabase, Neon)
- To switch to PostgreSQL, update `DATABASE_URL`:
  ```
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  ```
- Add `psycopg2-binary` to requirements.txt if using PostgreSQL:
  ```
  psycopg2-binary==2.9.9
  ```

### ChromaDB Vectorstore

- ChromaDB persists to the `vectorstore/` directory using HuggingFace embeddings (`all-MiniLM-L6-v2`)
- On first request, the app loads documents from `documents/` and creates the vectorstore
- **On ephemeral storage:** The vectorstore is rebuilt every deploy (takes 10–30 seconds for a few documents)
- **Workaround for ephemeral platforms:** Store the vectorstore in a cloud bucket (S3, R2) and download on startup, or switch to a cloud vector database like Pinecone or Chroma Cloud
- The vectorstore directory can grow large if you upload many documents (the `all-MiniLM-L6-v2` embeddings are ~90 MB)

### Documents Folder

- Place `.pdf` or `.txt` fitness documents in the `documents/` folder
- The app reads these during vectorstore creation
- With no documents, the RAG pipeline returns `None` and the app works in LLM-only mode
- Sample documents: workout plans, nutrition guides, exercise form guides

### Security Checklist

For production, change these from default values:

| Item | Default | Recommendation |
|------|---------|----------------|
| `SECRET_KEY` | `fitgenie-default-secret-key` | Generate a 64-char hex key |
| `debug=True` | True | Set to `False` in production |
| `SQLALCHEMY_DATABASE_URI` | SQLite | Use PostgreSQL for production |
| Session cookies | HTTP only | Already configured in Flask by default |

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Platform Free Tier Limits Comparison

| Platform | RAM | Storage | Sleep after idle | Custom domain |
|----------|-----|---------|-----------------|---------------|
| PythonAnywhere | 512 MB | 500 MB | No | No (paid only) |
| Render | 512 MB | 1 GB (disk) | 15 min | No (paid only) |
| Railway | ~512 MB | 1 GB (volume) | No | No (paid only) |
| Koyeb | 1 GB | 1 GB | No | Yes |
| Oracle Cloud | 24 GB | 200 GB | No | Yes |

### Production Readiness Tips

1. **Use Gunicorn** with multiple workers:
   ```bash
   gunicorn --workers 2 --bind 0.0.0.0:8000 --timeout 120 app:app
   ```

2. **Use Flask-Migrate** for database schema changes:
   ```bash
   pip install Flask-Migrate
   ```
   Then in `app.py`:
   ```python
   from flask_migrate import Migrate
   migrate = Migrate(app, db)
   ```

3. **Monitor usage** on free tiers:
   - PythonAnywhere: 100 sec/day of CPU for PythonAnywhere free
   - Render: 750 hours/month of runtime (but sleeps after inactivity)
   - Railway: $5 credit/month (~500 hours of runtime)
   - OpenAI API: Set usage limits at https://platform.openai.com/account/limits

4. **Logging**: Add proper logging for production:
   ```python
   import logging
   logging.basicConfig(filename='fitgenie.log', level=logging.INFO)
   ```

5. **Rate limiting** (optional for production):
   ```bash
   pip install flask-limiter
   ```

---

## Quick Reference: Platform Configuration Files

### Procfile (for Render, Railway, Heroku)

Create `Procfile` in project root:

```procfile
web: gunicorn app:app
```

### runtime.txt (for PythonAnywhere, Render, Heroku)

Create `runtime.txt` in project root:

```
python-3.11.7
```

### nixpacks.toml (for Railway)

Create `nixpacks.toml` in project root:

```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn app:app"
```

### Dockerfile (for Koyeb, custom servers)

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ChromaDB and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create persistent data directories
RUN mkdir -p /data/instance /data/documents /data/vectorstore

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
```

### render-init.sh (for Render persistent disk)

Create `render-init.sh` in project root:

```bash
#!/bin/bash
set -e

echo "=== Render Init Script ==="

# Create persistent directories on mounted disk
mkdir -p /var/data/instance
mkdir -p /var/data/documents
mkdir -p /var/data/vectorstore

echo "Directories created at /var/data/"

# Initialize the database
python -c "
from app import app, db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/data/instance/database.db'
app.app_context().push()
db.create_all()
print('Database tables created successfully')
"

echo "=== Init complete ==="
```

Make it executable:
```bash
chmod +x render-init.sh
```

---

## Final Checklist

Before considering your deployment complete, verify:

- [ ] App loads without errors
- [ ] Registration and login work
- [ ] Dashboard shows after login
- [ ] BMI calculator works
- [ ] Chat interface works (or falls back gracefully)
- [ ] Document upload works
- [ ] Environment variables are set (not hardcoded)
- [ ] `SECRET_KEY` is a strong random value
- [ ] `debug=False` in production
- [ ] Static files (CSS/JS) load correctly
- [ ] Database persists across restarts
- [ ] Vectorstore persists or rebuilds correctly
- [ ] OpenAI API key is valid (if used)
