FROM python:3.12.2 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv --copies .venv

COPY requirements.txt ./
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12.2-slim
# Create a non-root user for Hugging Face compatibility
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy the virtual environment with --copies to avoid absolute path issues
COPY --from=builder --chown=user /app/.venv .venv/
COPY --chown=user . .

# HF Spaces uses port 7860
# Use explicit python -m uvicorn to avoid shebang path issues
CMD [".venv/bin/python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
