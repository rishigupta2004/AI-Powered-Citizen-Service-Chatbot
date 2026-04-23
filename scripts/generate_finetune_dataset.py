"""
Generate Sarvam-M fine-tune dataset from SevaSindhu DB.
Outputs: data/finetune_dataset.jsonl
Format: {"prompt": "...", "completion": "..."}
"""
import os, sys, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2

DB_URL = os.environ['DATABASE_URL'].replace('postgresql+psycopg2://', 'postgresql://')
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

SYSTEM = (
    "You are SevaSindhu AI, an expert assistant for Indian government services. "
    "Answer clearly and accurately in the user's language. "
    "Cite specific documents, fees, and timelines when known."
)

pairs = []

# Source 1: FAQs — direct Q/A pairs (highest quality)
cur.execute("SELECT question, answer, short_answer FROM faqs WHERE question IS NOT NULL AND answer IS NOT NULL")
for q, a, short_a in cur.fetchall():
    pairs.append({
        "prompt": f"<s>[INST] <<SYS>>\n{SYSTEM}\n<</SYS>>\n\n{q} [/INST]",
        "completion": f" {a} </s>"
    })
    if short_a:
        pairs.append({
            "prompt": f"<s>[INST] <<SYS>>\n{SYSTEM}\n<</SYS>>\n\nBriefly: {q} [/INST]",
            "completion": f" {short_a} </s>"
        })

print(f"FAQs: {len(pairs)} pairs")

# Source 2: Content chunks — synthetic Q/A from passages
cur.execute("""
    SELECT cc.chunk_text, s.name
    FROM content_chunks cc
    JOIN services s ON cc.service_id = s.service_id
    WHERE cc.chunk_text IS NOT NULL
    AND length(cc.chunk_text) > 100
    LIMIT 500
""")
chunk_pairs_before = len(pairs)
for chunk_text, service_name in cur.fetchall():
    # Generate question from chunk
    q = f"What are the requirements for {service_name}?"
    pairs.append({
        "prompt": f"<s>[INST] <<SYS>>\n{SYSTEM}\n<</SYS>>\n\n{q} [/INST]",
        "completion": f" {chunk_text[:800]} </s>"
    })

print(f"Chunks: {len(pairs)-chunk_pairs_before} pairs")
print(f"Total: {len(pairs)} training pairs")

# Save
out = Path(__file__).parent.parent / "data" / "finetune_dataset.jsonl"
out.parent.mkdir(exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + '\n')

print(f"✅ Saved to {out}")
print(f"   File size: {out.stat().st_size / 1024:.1f} KB")

conn.close()
