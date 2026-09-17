from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    company: str
    title: str
    location: str
    url: str
    work_mode: str | None = None
    compensation: str | None = None


def dedupe_jobs(jobs: list[Job]) -> list[Job]:
    seen: set[str] = set()
    result: list[Job] = []

    for job in jobs:
        key = job.url.strip().lower().split("#", 1)[0]
        if key not in seen:
            seen.add(key)
            result.append(job)

    return result
