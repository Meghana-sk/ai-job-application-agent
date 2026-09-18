from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from src.search.providers import ProviderJob

def prepare_application(job: ProviderJob, evaluation: dict, output_dir: str = "data/prepared") -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = Path(output_dir) / f"{job.provider}-{job.provider_job_id}.json"
    payload = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_approval",
        "provider": job.provider,
        "provider_job_id": job.provider_job_id,
        "company": job.company,
        "role": job.title,
        "location": job.location,
        "work_mode": job.work_mode,
        "job_url": job.url,
        "apply_url": job.apply_url,
        "match": evaluation,
        "submission": {"mode": "approval_required", "reason": "External submission may require sensitive fields, authentication, CAPTCHA, or MFA."},
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)
