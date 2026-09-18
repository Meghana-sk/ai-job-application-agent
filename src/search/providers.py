from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html import unescape


@dataclass(frozen=True)
class ProviderJob:
    provider: str
    provider_job_id: str
    company: str
    title: str
    location: str
    work_mode: str | None
    description: str
    url: str
    apply_url: str
    compensation: str | None = None


def _get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ai-job-application-agent/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def greenhouse_jobs(board: str) -> list[ProviderJob]:
    data = _get_json(
        f"https://boards-api.greenhouse.io/v1/boards/{urllib.parse.quote(board)}/jobs?content=true"
    )
    result = []
    for item in data.get("jobs", []):
        location = (item.get("location") or {}).get("name", "")
        result.append(
            ProviderJob(
                provider="greenhouse",
                provider_job_id=str(item.get("id")),
                company=board,
                title=item.get("title", ""),
                location=location,
                work_mode=None,
                description=_text(item.get("content")),
                url=item.get("absolute_url", ""),
                apply_url=item.get("absolute_url", ""),
            )
        )
    return result


def lever_jobs(site: str) -> list[ProviderJob]:
    url = f"https://api.lever.co/v0/postings/{urllib.parse.quote(site)}?mode=json"
    data = _get_json(url)
    result = []
    for item in data if isinstance(data, list) else data.get("data", []):
        categories = item.get("categories") or {}
        location = categories.get("location") or ", ".join(categories.get("allLocations") or [])
        result.append(
            ProviderJob(
                provider="lever",
                provider_job_id=str(item.get("id")),
                company=site,
                title=item.get("text", ""),
                location=location,
                work_mode=item.get("workplaceType"),
                description=_text(item.get("description")),
                url=item.get("hostedUrl") or item.get("urls", {}).get("show", ""),
                apply_url=item.get("applyUrl") or item.get("urls", {}).get("apply", ""),
                compensation=item.get("salaryDescription"),
            )
        )
    return result


def discover(config: dict[str, list[str]]) -> list[ProviderJob]:
    jobs: list[ProviderJob] = []
    for board in config.get("greenhouse", []):
        try:
            jobs.extend(greenhouse_jobs(board))
        except Exception as exc:
            print(f"Greenhouse board {board!r} failed: {exc}")
    for site in config.get("lever", []):
        try:
            jobs.extend(lever_jobs(site))
        except Exception as exc:
            print(f"Lever site {site!r} failed: {exc}")
    return jobs
