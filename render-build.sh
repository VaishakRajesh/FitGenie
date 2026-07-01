#!/usr/bin/env bash
# Render build script - handles Rust/cargo read-only filesystem issue
set -o errexit

# Prevent tiktoken from trying to build Rust extension
export TIKTOKEN_ENABLE_EXTENSION=0

pip install --upgrade pip
pip install -r requirements.txt

# Download sentence-transformers model cache at build time
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || true
