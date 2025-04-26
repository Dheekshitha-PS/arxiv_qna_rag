#!/bin/bash
set -e

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to become healthy..."
until curl -s http://localhost:11434/tags >/dev/null; do
  echo "Still waiting..."
  sleep 2
done
echo "Ollama is up!"

# Pull required models
echo "Pulling required models..."
ollama pull mistral || echo "Failed to pull mistral model"
ollama pull llama3 || echo "Failed to pull llama3 model"
ollama pull nomic-embed-text:latest || echo "Failed to pull nomic-embed-text model"

# Wait for background processes
wait
