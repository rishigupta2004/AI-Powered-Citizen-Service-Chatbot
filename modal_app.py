"""
Modal deployment for Seva Sindhu FastAPI backend.

Usage:
  .venv/bin/python -m modal deploy modal_app.py
"""

import modal

# ── Modal app & image ──────────────────────────────────────────────────────────

app = modal.App("seva-sindhu-backend")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install(
        "libpq-dev",          # psycopg2
        "tesseract-ocr",      # pytesseract
        "libgl1",             # opencv
        "libglib2.0-0",       # opencv
    )
    .pip_install_from_requirements("requirements.txt")
    # Bake project files into the image
    .add_local_dir("core", remote_path="/app/core")
    .add_local_dir("routes", remote_path="/app/routes")
    .add_local_dir("data", remote_path="/app/data")
    .add_local_file("app.py", remote_path="/app/app.py")
    .add_local_file(".env.example", remote_path="/app/.env.example")
)

# ── Secrets ────────────────────────────────────────────────────────────────────
# Create a secret group called "seva-sindhu" in the Modal dashboard:
#   https://modal.com/secrets
#
# Required keys:
#   DATABASE_URL, SARVAM_API_KEY, HF_TOKEN, JWT_SECRET_KEY,
#   VITE_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, CLERK_DOMAIN, JWKS_URL

secrets = modal.Secret.from_name("seva-sindhu")


# ── ASGI entrypoint ───────────────────────────────────────────────────────────

@app.function(
    image=image,
    secrets=[secrets],
    # min_containers=1 means one container is always ready — no cold starts
    # Set to 0 to save credits and tolerate ~5s cold starts
    min_containers=1,
    timeout=300,
    cpu=0.25,
    memory=512,
)
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def fastapi_entrypoint():
    """Serve the FastAPI app on Modal."""
    import os
    import sys

    os.chdir("/app")
    sys.path.insert(0, "/app")

    # Add the Modal URL to CORS origins
    existing_cors = os.getenv("CORS_ORIGINS", "")
    extra_origins = ",".join(filter(None, [
        existing_cors,
        "https://seva-sindu-portal.vercel.app",
    ]))
    os.environ["CORS_ORIGINS"] = extra_origins

    from app import app as fastapi_app
    return fastapi_app
