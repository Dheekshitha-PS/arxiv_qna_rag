FROM ollama/ollama
# Install curl
RUN apt-get update && apt-get install -y curl

# Optional: add a script to pull models on startup
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
