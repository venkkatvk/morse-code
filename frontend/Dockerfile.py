# ==========================================
# STAGE 1: The UI Builder
# ==========================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# STAGE 2: The UI Runner
# ==========================================
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/visuser/.local/bin:$PATH

WORKDIR /workspace

# Enforce security boundaries with an isolated non-root user
RUN groupadd -g 8889 visgroup && \
    useradd -u 8889 -g visgroup -m -s /bin/bash visuser

COPY --from=builder /root/.local /home/visuser/.local
COPY frontend/ ./frontend/

RUN chown -R visuser:visgroup /workspace /home/visuser
USER visuser

EXPOSE 8501

# Execute the interface canvas bound to the container network
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]