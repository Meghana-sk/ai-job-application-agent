from __future__ import annotations
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import psycopg
from psycopg.types.json import Jsonb
from .status import ApplicationStatus

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class ApplicationStore:
    """Private PostgreSQL tracker and candidate-profile store."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.getenv("DATABASE_URL") or os.getenv("APPLICATION_DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL or APPLICATION_DATABASE_URL is required")
        self.connection = psycopg.connect(self.database_url)
        self.connection.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.connection.commit()

    def get_candidate_profile(self) -> dict[str, Any]:
        row = self.connection.execute(
            """SELECT profile_id, full_name, email, phone, linkedin_url, github_url,
                      target_roles, preferences, compensation, experience, skills, application_answers
               FROM private.candidate_profile WHERE profile_id = 'default'"""
        ).fetchone()
        if not row:
            raise RuntimeError("private.candidate_profile/default is missing")
        return {
            "profile_id": row[0], "full_name": row[1], "email": row[2], "phone": row[3],
            "linkedin_url": row[4], "github_url": row[5], "target_roles": row[6],
            "preferences": row[7], "compensation": row[8], "experience": row[9],
            "skills": row[10], "application_answers": row[11],
        }

    def add_application(self, record: dict[str, Any]) -> bool:
        now = utc_now()
        cur = self.connection.execute(
            """INSERT INTO applications (
                application_id, job_id, company, role, location, work_mode,
                application_url, source, discovered_at, role_match,
                matched_skills, missing_skills, match_score,
                compensation_value_inr, compensation_currency,
                compensation_disclosed, status, prepared_at, submitted_at,
                submission_reference, first_seen_at, last_updated_at,
                duplicate_of, error_code, error_message, notes
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (application_id) DO NOTHING""",
            (
                record["application_id"], record.get("job_id"), record.get("company", ""),
                record.get("role", ""), record.get("location"), record.get("work_mode"),
                record.get("application_url"), record.get("source"), record.get("discovered_at", now),
                record.get("role_match"), Jsonb(record.get("matched_skills", [])),
                Jsonb(record.get("missing_skills", [])), record.get("match_score"),
                record.get("compensation_value_inr"), record.get("compensation_currency", "INR"),
                bool(record.get("compensation_disclosed", False)), record.get("status", ApplicationStatus.DISCOVERED.value),
                record.get("prepared_at"), record.get("submitted_at"), record.get("submission_reference"),
                record.get("first_seen_at", now), record.get("last_updated_at", now),
                record.get("duplicate_of"), record.get("error_code"), record.get("error_message"),
                record.get("notes"),
            ),
        )
        inserted = cur.rowcount == 1
        self.connection.commit()
        return inserted

    def record_status(self, application_id: str, status: ApplicationStatus | str, details: str | None = None) -> None:
        value = status.value if isinstance(status, ApplicationStatus) else status
        now = utc_now()
        self.connection.execute(
            """UPDATE applications SET status=%s,last_updated_at=%s,
               prepared_at=CASE WHEN %s='prepared' THEN COALESCE(prepared_at,%s) ELSE prepared_at END,
               submitted_at=CASE WHEN %s='submitted' THEN COALESCE(submitted_at,%s) ELSE submitted_at END
               WHERE application_id=%s""",
            (value, now, value, now, value, now, application_id),
        )
        self.connection.execute(
            "INSERT INTO application_events (application_id,status,timestamp,details) VALUES (%s,%s,%s,%s)",
            (application_id, value, now, details),
        )
        self.connection.commit()

    def metrics_since(self, since: str) -> dict[str, int]:
        row = self.connection.execute(
            """SELECT COUNT(DISTINCT CASE WHEN status='discovered' THEN application_id END),
                      COUNT(DISTINCT CASE WHEN status='matched' THEN application_id END),
                      COUNT(DISTINCT CASE WHEN status='prepared' THEN application_id END),
                      COUNT(DISTINCT CASE WHEN status='submitted' THEN application_id END),
                      COUNT(DISTINCT CASE WHEN status='failed' THEN application_id END)
               FROM application_events WHERE timestamp >= %s""", (since,)
        ).fetchone()
        return {"jobs_found":int(row[0] or 0),"matching_jobs":int(row[1] or 0),
                "applications_prepared":int(row[2] or 0),"applications_submitted":int(row[3] or 0),
                "errors":int(row[4] or 0)}

    def close(self) -> None:
        self.connection.close()
