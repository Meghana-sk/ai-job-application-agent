from __future__ import annotations

import os
from dataclasses import dataclass


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

    if not config.enabled:
        print("Job search is disabled.")
        return

    print("AI Job Application Agent")
    print(f"Discovery limit: {config.max_results}")
    print("Safe discovery pipeline initialized.")
    print("Add an authorized job-provider integration to perform live searches.")


if __name__ == "__main__":
    run()
