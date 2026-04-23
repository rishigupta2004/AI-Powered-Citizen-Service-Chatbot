# Hugging Face Spaces Deployment

## One-time HF CLI Setup
```bash
pip install huggingface_hub
hf login
```

## Deploy with Secrets
```bash
# Navigate to project
cd gov-chatbot

# Set all secrets at once from .hf_secrets file
while IFS='=' read -r key value; do
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  hf space secret set "$key=$value"
done < .hf_secrets

# Or set individually:
hf space secret set DATABASE_URL="postgresql://postgres:mejQo3-gyjxes-curgux@db.qqzanqrgrwrsmiuhxrvn.supabase.co:5432/postgres"
hf space secret set SARVAM_API_KEY="sk_h3gz0bjv_0zmbS684fiReZAnVUpXsygZU"
hf space secret set HF_TOKEN="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"
```

## Rebuild Space
After setting secrets, go to HF Spaces settings and click "Rebuild"

## Verify Deployment
Check logs: HF Spaces -> Settings -> Logs
Health check: curl https://your-space.huggingface.co/health