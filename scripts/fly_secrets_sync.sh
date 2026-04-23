#!/usr/bin/env bash
set -euo pipefail

# Sync required secrets to Fly.io.
# Default: dry-run (prints commands only)
# Apply:   ./scripts/fly_secrets_sync.sh --apply

APP_NAME="${FLY_APP_NAME:-gov-chatbot}"
APPLY=false

if [[ "${1:-}" == "--apply" ]]; then
  APPLY=true
fi

SECRETS=(
  "DATABASE_URL=${DATABASE_URL:-postgresql+psycopg2://postgres:postgres@localhost:5432/citizen_services_dev}"
  "EMBEDDING_DIM=${EMBEDDING_DIM:-384}"
  "SECRET_KEY=${SECRET_KEY:-change-this-in-production-use-openssl-rand-hex-32}"
  "JWT_ALGORITHM=${JWT_ALGORITHM:-RS256}"
  "FRONTEND_URL=${FRONTEND_URL:-https://your-frontend-domain.example}"
  "API_KEY=${API_KEY:-optional-admin-api-key}"
  "SARVAM_API_KEY=${SARVAM_API_KEY:-your_sarvam_key_here}"
  "CLERK_SECRET_KEY=${CLERK_SECRET_KEY:-sk_test_replace_me}"
  "CLERK_PUBLISHABLE_KEY=${CLERK_PUBLISHABLE_KEY:-pk_test_replace_me}"
  "CLERK_PUBLIC_KEY=${CLERK_PUBLIC_KEY:-pk_test_replace_me}"
  "CLERK_PUBLIC_KE=${CLERK_PUBLIC_KE:-pk_test_replace_me}"
  "CLERK_FRONTEND_API_URL=${CLERK_FRONTEND_API_URL:-https://your-clerk-domain.clerk.accounts.dev}"
  "CLERK_Frontend_API_URL=${CLERK_Frontend_API_URL:-https://your-clerk-domain.clerk.accounts.dev}"
  "CLERK_BACKEND_API_URL=${CLERK_BACKEND_API_URL:-https://api.clerk.com}"
  "CLERK_Backend_API_URL=${CLERK_Backend_API_URL:-https://api.clerk.com}"
  "CLERK_JWKS_URL=${CLERK_JWKS_URL:-https://your-clerk-domain.clerk.accounts.dev/.well-known/jwks.json}"
  "JWKS_URL=${JWKS_URL:-https://your-clerk-domain.clerk.accounts.dev/.well-known/jwks.json}"
  "JWKS_PUBLIC_KEY=${JWKS_PUBLIC_KEY:-}"
  "JWKS_Public_Key=${JWKS_Public_Key:-}"
  "VITE_CLERK_PUBLISHABLE_KEY=${VITE_CLERK_PUBLISHABLE_KEY:-pk_test_replace_me}"
  "VITE_API_URL=${VITE_API_URL:-https://gov-chatbot.fly.dev}"
)

echo "Fly app: ${APP_NAME}"
if ${APPLY}; then
  echo "Mode: APPLY"
else
  echo "Mode: DRY-RUN (pass --apply to execute)"
fi

for secret in "${SECRETS[@]}"; do
  if ${APPLY}; then
    flyctl secrets set "${secret}" -a "${APP_NAME}"
  else
    echo "flyctl secrets set \"${secret}\" -a \"${APP_NAME}\""
  fi
done

echo "Done."
