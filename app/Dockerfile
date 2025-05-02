# Use a Python base image
FROM python:3.10-slim

# Set environment variable for non-interactive mode to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install dependencies and required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face model during build time to avoid runtime download
# Set the environment variable for HF cache directory
ENV HF_HOME=/app/.cache/huggingface

# Create the directory explicitly
RUN mkdir -p /app/.cache/huggingface

# Pre-download model and tokenizer into this directory
RUN python -c "\
from transformers import AutoModel, AutoTokenizer; \
AutoTokenizer.from_pretrained('BAAI/bge-base-en-v1.5', cache_dir='/app/.cache/huggingface'); \
AutoModel.from_pretrained('BAAI/bge-base-en-v1.5', cache_dir='/app/.cache/huggingface')"

# Copy the rest of the application files
COPY . .

# Expose the port for the app (default for Cloud Run is 8080)
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
