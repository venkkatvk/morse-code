# ==========================================
# STAGE 1: The Dependency Blacksmith (Builder)
# ==========================================
FROM python:3.11-slim AS builder

# Set systemic optimization variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install basic system build tools needed for heavy libraries like numpy/scipy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency sheets to utilize Docker layer caching efficiently
COPY requirements.txt .

# Compile and isolate wheels into the local user space namespace
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# STAGE 2: The Production Courier (Runner)
# ==========================================
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/opsuser/.local/bin:$PATH

WORKDIR /workspace

# Create a secure, restricted non-root group and system user
RUN groupadd -g 8888 opsgroup && \
    useradd -u 8888 -g opsgroup -m -s /bin/bash opsuser

# Extract only the pristine compiled packages from our Builder stage
COPY --from=builder /root/.local /home/opsuser/.local

# Copy the core application mechanics and shift ownership to our unprivileged user
COPY app/ ./app/
RUN chown -R opsuser:opsgroup /workspace /home/opsuser

# Lower privilege gates for security hardening
USER opsuser

EXPOSE 8000

# Execute the ASGI application cluster
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]