from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .status import ApplicationStatus

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ApplicationStore:
    """Private local SQLite tracker for job discovery/application state."""

    def __init__(self, db_path: str | Path = "data/applications.sqlite3") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.connection.commit()

    def add_application(self, record: dict[str, Any]) -> None:
        now = utc_now()
        matching = record.get("matching", {})
        compensation = matching.get("compensation", {})
        application = record.get("application", {})
        tracking = record.get("tracking", {})

        self.connection.execute(
            """
            INSERT INTO applications (
                application_id, job_id, company, role, location, work_mode,
                application_url, source, discovered_at, role_match,
                matched_skills, missing_skills, match_score,
                compensation_value_inr, compensation_currency,
                compensation_disclosed, status, prepared_at, submitted_at,
                submission_reference, first_seen_at, last_updated_at,
                duplicate_of, error_code, error_message, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["application_id"],
                record.get("job", {}).get("job_id"),
                record.get("job", {}).get("company", ""),
                record.get("job", {}).get("role", ""),
                record.get("job", {}).get("location"),
                record.get("job", {}).get("work_mode"),
                record.get("job", {}).get("application_url"),
                record.get("job", {}).get("source"),
                record.get("job", {}).get("discovered_at", now),
                int(bool(matching.get("role_match"))) if "role_match" in matching else None,
                json.dumps(matching.get("matched_skills", [])),
                json.dumps(matching.get("missing_skills", [])),
                matching.get("score"),
                compensation.get("value_inr"),
                compensation.get("currency", "INR"),
                int(bool(compensation.get("disclosed", False))),
                application.get("status", ApplicationStatus.DISCOVERED.value),
                application.get("prepared_at"),
                application.get("submitted_at"),
                application.get("submission_reference"),
                tracking.get("first_seen_at", now),
                tracking.get("last_updated_at", now),
                tracking.get("duplicate_of"),
                record.get("error", {}).get("code"),
                record.get("error", {}).get("message"),
                record.get("notes"),
            ),
        )
        self.connection.execute(
            "INSERT INTO application_events (application_id, status, timestamp) VALUES (?, ?, ?)",
            (
                record["application_id"],
                application.get("status", ApplicationStatus.DISCOVERED.value),
                now,
            ),
        )
        self.connection.commit()

    def record_status(
        self,
        application_id: str,
        status: ApplicationStatus | str,
        details: str | None = None,
    ) -> None:
        value = status.value if isinstance(status, ApplicationStatus) else status
        now = utc_now()
        self.connection.execute(
            """
            UPDATE applications
            SET status = ?, last_updated_at = ?,
                prepared_at = CASE WHEN ? = 'prepared' THEN COALESCE(prepared_at, ?) ELSE prepared_at END,
                submitted_at = CASE WHEN ? = 'submitted' THEN COALESCE(submitted_at, ?) ELSE submitted_at END
            WHERE application_id = ?
            """,
            (value, now, value, now, value, now, application_id),
        )
        self.connection.execute(
            """
            INSERT INTO application_events (application_id, status, timestamp, details)
            VALUES (?, ?, ?, ?)
            """,
            (application_id, value, now, details),
        )
        self.connection.commit()

    def metrics_since(self, since: str) -> dict[str, int]:
        """Return current-run metrics based on status events after the supplied timestamp."""
        row = self.connection.execute(
            """
            SELECT
                COUNT(DISTINCT CASE WHEN status = 'discovered' THEN application_id END),
                COUNT(DISTINCT CASE WHEN status = 'matched' THEN application_id END),
                COUNT(DISTINCT CASE WHEN status = 'prepared' THEN application_id END),
                COUNT(DISTINCT CASE WHEN status = 'submitted' THEN application_id END),
                COUNT(DISTINCT CASE WHEN status = 'failed' THEN application_id END)
            FROM application_events
            WHERE timestamp >= ?
            """,
            (since,),
        ).fetchone()

        return {
            "jobs_found": int(row[0] or 0),
            "matching_jobs": int(row[1] or 0),
            "applications_prepared": int(row[2] or 0),
            "applications_submitted": int(row[3] or 0),
            "errors": int(row[4] or 0),
        }

    def close(self) -> None:
        self.connection.close()
