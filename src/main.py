from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

from src.reporting.summary import write_metrics
from src.tracking.store import ApplicationStore


@dataclass
class SearchConfig:
    max_results: int = 10
    enabled: bool = True


def load_config() -> SearchConfig:
    enabled = os.getenv("JOB_SEARCH_ENABLED", "true").lower() == "true"
    max_results = int(os.getenv("JOB_SEARCH_MAX_RESULTS", "10"))
    return SearchConfig(max_results=max_results, enabled=enabled)


def run() -> None:
    config = load_config()
    run_started_at = datetime.now(timezone.utc).isoformat()

    if not config.enabled:
        write_metrics({
            "jobs_found": 0,
            "matching_jobs": 0,
            "applications_prepared": 0,
            "applications_submitted": 0,
            "errors": 0,
        })
        print("Job search is disabled.")
        return

    store = ApplicationStore()
    try:
        print("AI Job Application Agent")
        print(f"Discovery limit: {config.max_results}")
        print("Safe discovery pipeline initialized.")
        print("Add an authorized job-provider integration to perform live searches.")

        # Future discovery/matching/application integrations should call
        # ApplicationStore as they progress. The summary counts those events.
        metrics = store.metrics_since(run_started_at)
        write_metrics(metrics)

        print(f"Jobs found: {metrics['jobs_found']}")
        print(f"Matching jobs: {metrics['matching_jobs']}")
        print(f"Applications prepared: {metrics['applications_prepared']}")
        print(f"Applications submitted: {metrics['applications_submitted']}")
        print(f"Errors: {metrics['errors']}")
    except Exception:
        write_metrics({
            "jobs_found": 0,
            "matching_jobs": 0,
            "applications_prepared": 0,
            "applications_submitted": 0,
            "errors": 1,
        })
        raise
    finally:
        store.close()


if __name__ == "__main__":
    run()
