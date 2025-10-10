import json
import os
import uuid
from datetime import datetime, date
from typing import Any, Dict, List

from sqlalchemy.orm import Session
import sqlalchemy as sa

from ..models import Service, Document, FAQ, ContentChunk, RawContent
from sqlalchemy.dialects.postgresql import UUID as PGUUID


def _to_json_safe(value: Any) -> Any:
    try:
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        # pgvector returns memoryview/bytes sometimes; coerce to list/str safely
        if hasattr(value, "tolist"):
            return value.tolist()
        if isinstance(value, (bytes, bytearray, memoryview)):
            try:
                return bytes(value).decode("utf-8", errors="ignore")
            except Exception:
                return str(value)
        # JSON-serializable values pass through
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def _model_to_dict(obj: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        data[col.name] = _to_json_safe(val)
    return data


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
                entities[name] = [{k: _to_json_safe(v) for k, v in dict(r).items()} for r in raw_rows]
            else:
                try:
                    stmt = sa.text(f"SELECT * FROM {model.__tablename__}")
                    raw_rows = session.execute(stmt).mappings().all()
                    entities[name] = [{k: _to_json_safe(v) for k, v in dict(r).items()} for r in raw_rows]
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

    def _coerce_for_model(model, row: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(row)
        # Remove auto-managed timestamp fields to avoid parsing issues
        for ts_field in ("created_at", "updated_at"):
            out.pop(ts_field, None)
        # Coerce UUID strings back to uuid.UUID
        try:
            for col in model.__table__.columns:
                if isinstance(col.type, PGUUID):
                    val = out.get(col.name)
                    if isinstance(val, str):
                        try:
                            out[col.name] = uuid.UUID(val)
                        except Exception:
                            pass
        except Exception:
            pass
        return out

    for model, name in mapping:
        rows = _load(name)
        restored_counts[name] = 0
        for row in rows:
            obj = model(**_coerce_for_model(model, row))
            session.merge(obj)  # upsert behavior
            restored_counts[name] += 1
        session.flush()

    session.commit()
    return {"restored_counts": restored_counts, "input_dir": input_dir}