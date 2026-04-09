# Stage 1: Get the Ollama binary from the official image
FROM ollama/ollama:latest AS ollama_source

# Stage 2: Build your Python environment
FROM python:3.11-slim

# Install minimal dependencies for model pulling and SSL
RUN apt-get update && apt-get install -y ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the binary from the first stage
COPY --from=ollama_source /usr/bin/ollama /usr/bin/ollama

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx

COPY main.py .

# RAM & Runtime Optimizations
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=0
ENV CUDA_VISIBLE_DEVICES=""

EXPOSE 8000

# Start Ollama, wait for it, pull model, then start FastAPI
CMD ["sh", "-c", "ollama serve & sleep 10 && ollama pull qwen2.5:1.5b && uvicorn main:app --host 0.0.0.0 --port 8000"]