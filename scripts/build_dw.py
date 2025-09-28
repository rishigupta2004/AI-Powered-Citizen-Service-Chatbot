import os
import hashlib
import datetime
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set in environment")
    return create_engine(database_url, echo=True, future=True)


def compute_text_hash(value: Optional[str]) -> str:
    data = (value or "").encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def ensure_dw_schema(engine: Engine) -> None:
    sql_path = os.path.join(os.path.dirname(__file__), "..", "database", "dw", "schema_dw.sql")
    sql_path = os.path.abspath(sql_path)
    with open(sql_path, "r", encoding="utf-8") as f:
        ddl_sql = f.read()
    with engine.begin() as conn:
        conn.exec_driver_sql(ddl_sql)


def yyyymmdd(dt: datetime.date) -> int:
    return dt.year * 10000 + dt.month * 100 + dt.day


def load_dim_service(engine: Engine) -> None:
    with engine.begin() as conn:
        rows = conn.execute(text(
            """
            SELECT service_id, name, category
            FROM services
            ORDER BY service_id
            """
        )).mappings().all()

        for r in rows:
            conn.execute(text(
                """
                SELECT dw.upsert_dim_service(:service_id_nk, :name, :category)
                """
            ), {
                "service_id_nk": r["service_id"],
                "name": r["name"],
                "category": r["category"],
            })


def load_dim_document(engine: Engine) -> None:
    with engine.begin() as conn:
        rows = conn.execute(text(
            """
            SELECT d.doc_id, d.service_id, d.name, d.description, d.mandatory,
                   d.source, d.file_name, d.language, d.doc_type
            FROM documents d
            ORDER BY d.doc_id
            """
        )).mappings().all()

        for r in rows:
            # language might be NULL or not in enum; coerce to safe value
            lang = (r["language"] or "en").lower()
            if lang not in {"en","hi","bn","ta","te","mr","gu","kn","ml","pa"}:
                lang = "en"
            conn.execute(text(
                """
                SELECT dw.upsert_dim_document(
                    :doc_id_nk, :service_id_nk, :name, :description, :mandatory,
                    :source, :file_name, :language, :doc_type
                )
                """
            ), {
                "doc_id_nk": r["doc_id"],
                "service_id_nk": r["service_id"],
                "name": r["name"],
                "description": r["description"],
                "mandatory": r["mandatory"],
                "source": r["source"],
                "file_name": r["file_name"],
                "language": lang,
                "doc_type": r["doc_type"],
            })


def load_dim_procedure(engine: Engine) -> None:
    with engine.begin() as conn:
        rows = conn.execute(text(
            """
            SELECT p.procedure_id, p.service_id, p.title, p.steps
            FROM procedures p
            ORDER BY p.procedure_id
            """
        )).mappings().all()

        for r in rows:
            steps_hash = compute_text_hash(r["steps"]) if r["steps"] is not None else ""
            conn.execute(text(
                """
                SELECT dw.upsert_dim_procedure(
                    :procedure_id_nk, :service_id_nk, :title, :steps_hash
                )
                """
            ), {
                "procedure_id_nk": r["procedure_id"],
                "service_id_nk": r["service_id"],
                "title": r["title"],
                "steps_hash": steps_hash,
            })


def load_fact_document_availability(engine: Engine, load_date: datetime.date) -> None:
    load_date_sk = yyyymmdd(load_date)
    with engine.begin() as conn:
        # ensure load date exists in dim_date
        conn.execute(text(
            """
            INSERT INTO dw.dim_date(date_sk, date_actual, year_num, quarter_num, month_num, day_num, day_of_week, is_weekend)
            VALUES (:date_sk, :date_actual, EXTRACT(YEAR FROM :date_actual)::INT,
                    EXTRACT(QUARTER FROM :date_actual)::INT, EXTRACT(MONTH FROM :date_actual)::INT,
                    EXTRACT(DAY FROM :date_actual)::INT, EXTRACT(DOW FROM :date_actual)::INT,
                    CASE WHEN EXTRACT(DOW FROM :date_actual)::INT IN (0,6) THEN TRUE ELSE FALSE END)
            ON CONFLICT (date_sk) DO NOTHING
            """
        ), {"date_sk": load_date_sk, "date_actual": load_date})

        # idempotency: remove existing rows for this load date
        conn.execute(text(
            """
            DELETE FROM dw.fact_document_availability WHERE load_date_sk = :load_date_sk
            """
        ), {"load_date_sk": load_date_sk})

        # Map ODS docs to current dimension keys
        rows = conn.execute(text(
            """
            SELECT d.doc_id, d.service_id, d.language, d.mandatory, d.source, d.doc_type,
                   ds.service_sk, dd.document_sk
            FROM documents d
            JOIN dw.dim_service ds ON ds.service_id_nk = d.service_id AND ds.is_current = TRUE
            JOIN dw.dim_document dd ON dd.doc_id_nk = d.doc_id AND dd.is_current = TRUE
            """
        )).mappings().all()

        for r in rows:
            lang = (r["language"] or "en").lower()
            if lang not in {"en","hi","bn","ta","te","mr","gu","kn","ml","pa"}:
                lang = "en"
            conn.execute(text(
                """
                INSERT INTO dw.fact_document_availability(
                    service_sk, document_sk, load_date_sk, language, mandatory, is_present, source, doc_type
                ) VALUES (
                    :service_sk, :document_sk, :load_date_sk, :language, :mandatory, TRUE, :source, :doc_type
                )
                """
            ), {
                "service_sk": r["service_sk"],
                "document_sk": r["document_sk"],
                "load_date_sk": load_date_sk,
                "language": lang,
                "mandatory": r["mandatory"],
                "source": r["source"],
                "doc_type": r["doc_type"],
            })


def load_fact_procedure_coverage(engine: Engine, load_date: datetime.date) -> None:
    load_date_sk = yyyymmdd(load_date)
    with engine.begin() as conn:
        conn.execute(text(
            """
            INSERT INTO dw.dim_date(date_sk, date_actual, year_num, quarter_num, month_num, day_num, day_of_week, is_weekend)
            VALUES (:date_sk, :date_actual, EXTRACT(YEAR FROM :date_actual)::INT,
                    EXTRACT(QUARTER FROM :date_actual)::INT, EXTRACT(MONTH FROM :date_actual)::INT,
                    EXTRACT(DAY FROM :date_actual)::INT, EXTRACT(DOW FROM :date_actual)::INT,
                    CASE WHEN EXTRACT(DOW FROM :date_actual)::INT IN (0,6) THEN TRUE ELSE FALSE END)
            ON CONFLICT (date_sk) DO NOTHING
            """
        ), {"date_sk": load_date_sk, "date_actual": load_date})

        # idempotency: remove existing rows for this load date
        conn.execute(text(
            """
            DELETE FROM dw.fact_procedure_coverage WHERE load_date_sk = :load_date_sk
            """
        ), {"load_date_sk": load_date_sk})

        rows = conn.execute(text(
            """
            SELECT p.procedure_id, p.service_id, p.title, p.steps,
                   ds.service_sk, dp.procedure_sk
            FROM procedures p
            JOIN dw.dim_service ds ON ds.service_id_nk = p.service_id AND ds.is_current = TRUE
            JOIN dw.dim_procedure dp ON dp.procedure_id_nk = p.procedure_id AND dp.is_current = TRUE
            """
        )).mappings().all()

        for r in rows:
            step_count = 0
            if r["steps"]:
                # naive step count: split by newline or numbered markers
                text_content = r["steps"]
                parts = [s for s in text_content.replace("\r", "").split("\n") if s.strip()]
                step_count = len(parts)
            conn.execute(text(
                """
                INSERT INTO dw.fact_procedure_coverage(
                    service_sk, procedure_sk, load_date_sk, has_steps, step_count
                ) VALUES (
                    :service_sk, :procedure_sk, :load_date_sk, :has_steps, :step_count
                )
                """
            ), {
                "service_sk": r["service_sk"],
                "procedure_sk": r["procedure_sk"],
                "load_date_sk": load_date_sk,
                "has_steps": bool(r["steps"]),
                "step_count": step_count,
            })


def build_dw() -> None:
    engine = get_engine()
    ensure_dw_schema(engine)

    # Load dimensions first
    load_dim_service(engine)
    load_dim_document(engine)
    load_dim_procedure(engine)

    # Load facts for today
    today = datetime.date.today()
    load_fact_document_availability(engine, today)
    load_fact_procedure_coverage(engine, today)


if __name__ == "__main__":
    build_dw()

