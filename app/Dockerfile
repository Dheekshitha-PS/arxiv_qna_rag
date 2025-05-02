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
RUN python -c "from transformers import AutoModel, AutoTokenizer; \
               AutoModel.from_pretrained('BAAI/bge-base-en-v1.5'); \
               AutoTokenizer.from_pretrained('BAAI/bge-base-en-v1.5')"

# Copy the rest of the application files
COPY . .

# Expose the port for the app (default for Cloud Run is 8080)
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
