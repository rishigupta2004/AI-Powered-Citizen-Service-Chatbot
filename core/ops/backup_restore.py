import json
import os
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session
import sqlalchemy as sa

from ..models import Service, Document, FAQ, ContentChunk, RawContent


def _model_to_dict(obj: Any) -> Dict[str, Any]:
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


def backup_database(session: Session, output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    snapshot_time = datetime.utcnow().isoformat()

    entities: Dict[str, List[Dict[str, Any]]] = {}
    for model, name in [
        (Service, "services"),
        (Document, "documents"),
        (FAQ, "faqs"),
        (ContentChunk, "content_chunks"),
        (RawContent, "raw_contents"),
    ]:
        try:
            rows = session.query(model).all()
            entities[name] = [_model_to_dict(r) for r in rows]
        except Exception:
            # Ensure the session is cleared from previous error state
            try:
                session.rollback()
            except Exception:
                pass
            # Fallback to raw SQL when model mapping doesn't match actual columns
            if model is ContentChunk:
                stmt = sa.text(
                    "SELECT chunk_id, uuid, content_text, service_id, embedding, created_at FROM content_chunks"
                )
                raw_rows = session.execute(stmt).mappings().all()
                entities[name] = [dict(r) for r in raw_rows]
            else:
                try:
                    stmt = sa.text(f"SELECT * FROM {model.__tablename__}")
                    raw_rows = session.execute(stmt).mappings().all()
                    entities[name] = [dict(r) for r in raw_rows]
                except Exception:
                    # Table may not exist yet; record empty dataset
                    entities[name] = []

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"snapshot_time": snapshot_time, "counts": {k: len(v) for k, v in entities.items()}}, f, indent=2)

    for name, rows in entities.items():
        path = os.path.join(output_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    return {"snapshot_time": snapshot_time, "output_dir": output_dir}


def restore_database(session: Session, input_dir: str) -> Dict[str, Any]:
    restored_counts: Dict[str, int] = {}

    def _load(name: str) -> List[Dict[str, Any]]:
        path = os.path.join(input_dir, f"{name}.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    mapping = [
        (Service, "services"),
        (Document, "documents"),
        (FAQ, "faqs"),
        (ContentChunk, "content_chunks"),
        (RawContent, "raw_contents"),
    ]

    for model, name in mapping:
        rows = _load(name)
        restored_counts[name] = 0
        for row in rows:
            obj = model(**row)
            session.merge(obj)  # upsert behavior
            restored_counts[name] += 1
        session.flush()

    session.commit()
    return {"restored_counts": restored_counts, "input_dir": input_dir}