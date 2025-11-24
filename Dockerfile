# Build stage: Install dependencies that may require compilation
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# Runtime stage: Minimal image with only runtime dependencies
FROM python:3.11-slim AS runtime

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=5001 \
    DATABASE_URL=sqlite:////data/expense_tracker.db \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Install only runtime dependencies (curl for healthcheck)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source
COPY . .

# Create a dedicated user to run the app and give it ownership of the project + data dir
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && mkdir -p /data \
    && chown -R appuser:appgroup /app /data /home/appuser/.local

USER appuser

VOLUME ["/data"]

EXPOSE 5001

CMD ["python", "app.py"]

