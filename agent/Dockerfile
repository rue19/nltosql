FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libaio1t64 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create models directory for optional Qwen GGUF
RUN mkdir -p /app/models

WORKDIR /app
COPY requirements.txt .

# Install Python deps: no HuggingFace model download needed.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
