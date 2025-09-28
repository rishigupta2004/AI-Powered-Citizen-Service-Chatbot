import os
import sys
from datetime import date, datetime

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_engine(env_var_name: str) -> Engine:
    url = os.getenv(env_var_name)
    if not url:
        raise RuntimeError(f"Missing environment variable: {env_var_name}")
    return create_engine(url, future=True)


def ensure_dim_date(dw_engine: Engine) -> None:
    today = date.today()
    date_key = int(today.strftime("%Y%m%d"))
    with dw_engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO dw.dim_date (date_key, date_value, year, quarter, month, day, day_of_week, is_weekend)
                VALUES (:date_key, :date_value, :year, :quarter, :month, :day, :dow, :is_weekend)
                ON CONFLICT (date_key) DO NOTHING
                """
            ),
            {
                "date_key": date_key,
                "date_value": today,
                "year": today.year,
                "quarter": (today.month - 1) // 3 + 1,
                "month": today.month,
                "day": today.day,
                "dow": today.isoweekday(),
                "is_weekend": today.isoweekday() >= 6,
            },
        )


def upsert_dim_tables(src_engine: Engine, dw_engine: Engine) -> None:
    with src_engine.connect() as src, dw_engine.begin() as dw:
        # Services
        services = src.execute(text("SELECT service_id, name, category, created_at FROM services")).all()
        for s in services:
            dw.execute(
                text(
                    """
                    INSERT INTO dw.dim_service (service_id, name, category, created_at)
                    VALUES (:service_id, :name, :category, :created_at)
                    ON CONFLICT (service_key) DO NOTHING
                    """
                ),
                {
                    "service_id": s.service_id,
                    "name": s.name,
                    "category": s.category,
                    "created_at": s.created_at,
                },
            )

        # Map service_id -> service_key
        service_map = {
            r.service_id: r.service_key
            for r in dw.execute(text("SELECT service_key, service_id FROM dw.dim_service"))
        }

        # Procedures
        procedures = src.execute(
            text("SELECT procedure_id, service_id, title FROM procedures")
        ).all()
        for p in procedures:
            dw.execute(
                text(
                    """
                    INSERT INTO dw.dim_procedure (procedure_id, service_id, title)
                    VALUES (:procedure_id, :service_id, :title)
                    ON CONFLICT (procedure_key) DO NOTHING
                    """
                ),
                {
                    "procedure_id": p.procedure_id,
                    "service_id": p.service_id,
                    "title": p.title,
                },
            )

        # Documents (join extra metadata if present)
        documents = src.execute(
            text(
                """
                SELECT d.doc_id, d.service_id, d.name, d.description, d.mandatory,
                       COALESCE(dm.language, 'en') AS language,
                       COALESCE(dm.doc_type, 'pdf') AS doc_type,
                       COALESCE(dm.source, 'unknown') AS source
                FROM documents d
                LEFT JOIN (
                    SELECT NULL::int AS doc_id, NULL::text AS language, NULL::text AS doc_type, NULL::text AS source
                ) dm ON FALSE
                """
            )
        ).all()
        for d in documents:
            dw.execute(
                text(
                    """
                    INSERT INTO dw.dim_document (doc_id, service_id, name, mandatory, language, doc_type, source)
                    VALUES (:doc_id, :service_id, :name, :mandatory, :language, :doc_type, :source)
                    ON CONFLICT (document_key) DO NOTHING
                    """
                ),
                {
                    "doc_id": d.doc_id,
                    "service_id": d.service_id,
                    "name": d.name,
                    "mandatory": d.mandatory,
                    "language": d.language,
                    "doc_type": d.doc_type,
                    "source": d.source,
                },
            )

        # Users
        users = src.execute(
            text("SELECT user_id, name, email, role FROM users")
        ).all()
        for u in users:
            dw.execute(
                text(
                    """
                    INSERT INTO dw.dim_user (user_id, name, email, role)
                    VALUES (:user_id, :name, :email, :role)
                    ON CONFLICT (user_key) DO NOTHING
                    """
                ),
                {"user_id": u.user_id, "name": u.name, "email": u.email, "role": u.role},
            )


def load_fact_service_content(dw_engine: Engine) -> None:
    today_key = int(date.today().strftime("%Y%m%d"))
    with dw_engine.begin() as dw:
        dw.execute(text("DELETE FROM dw.fact_service_content WHERE date_key = :dk"), {"dk": today_key})
        dw.execute(
            text(
                """
                INSERT INTO dw.fact_service_content (date_key, service_key, procedure_count, document_count, faq_count, language_coverage)
                SELECT :dk AS date_key,
                       s.service_key,
                       COUNT(DISTINCT p.procedure_key) AS procedure_count,
                       COUNT(DISTINCT d.document_key) AS document_count,
                       COUNT(DISTINCT f.faq_id) AS faq_count,
                       COUNT(DISTINCT d.language) FILTER (WHERE d.language IS NOT NULL) AS language_coverage
                FROM dw.dim_service s
                LEFT JOIN dw.dim_procedure p ON p.service_id = s.service_id
                LEFT JOIN dw.dim_document d ON d.service_id = s.service_id
                LEFT JOIN (
                    SELECT service_id, MIN(faq_id) AS faq_id
                    FROM public.faqs
                    GROUP BY service_id
                ) f ON f.service_id = s.service_id
                GROUP BY s.service_key
                """
            ),
            {"dk": today_key},
        )


def main() -> None:
    try:
        src_engine = get_engine("DATABASE_URL")  # operational DB
        dw_engine = src_engine  # same database instance but different schema is fine
    except Exception as exc:
        print(f"[FATAL] Engine initialization failed: {exc}")
        sys.exit(1)

    # Ensure DW schema objects exist (assumes database/dw_schema.sql applied separately)
    ensure_dim_date(dw_engine)
    upsert_dim_tables(src_engine, dw_engine)
    load_fact_service_content(dw_engine)

    print("DW ETL completed successfully")


if __name__ == "__main__":
    main()

