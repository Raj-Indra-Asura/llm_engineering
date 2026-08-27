FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Ingest knowledge base
RUN python -m gridlens.rag.ingest

# Expose ports
EXPOSE 8000 7860

# Default: run API
CMD ["uvicorn", "gridlens.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
