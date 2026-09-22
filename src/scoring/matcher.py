from __future__ import annotations
import re
from src.matching.matcher import match_skills
from src.matching.profile import candidate_skills, role_keywords
from src.search.providers import ProviderJob

def _is_bengaluru(location: str) -> bool:
    value=(location or "").casefold()
    return "bengaluru" in value or "bangalore" in value

def _compensation_inr(description: str) -> int | None:
    text=description.replace(",","")
    matches=re.findall(r"(?:₹|rs\.?|inr\s*)(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lakhs)",text,re.I)
    return int(max(float(x) for x in matches)*100000) if matches else None

def _explicit_year_requirement(text: str) -> float | None:
    matches=re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",text,re.I)
    return max((float(x) for x in matches),default=None)

def evaluate(job: ProviderJob, minimum_compensation_inr: int, profile: dict | None = None) -> dict:
    title,description=job.title.casefold(),job.description.casefold()
    role_match=any(k in title for k in role_keywords(profile))
    skills=candidate_skills(profile)
    mentioned=[s for s in skills if s.casefold() in description or s.casefold() in title]
    skill_result=match_skills(mentioned,skills)
    compensation=_compensation_inr(job.description)
    compensation_ok=compensation is not None and compensation>=minimum_compensation_inr
    prefs=(profile or {}).get("preferences",{})
    remote_allowed=bool(prefs.get("remote_outside_bengaluru",True))
    location_ok=_is_bengaluru(job.location) or (remote_allowed and (job.work_mode or "").casefold()=="remote")
    experience=(profile or {}).get("experience",{})
    total_years=float(experience.get("total_years",0) or 0)
    staff_review=False
    if "staff" in title:
        required_years=_explicit_year_requirement(job.description)
        if required_years is not None and required_years>total_years:
            staff_review=True
    score=(30 if role_match else 0)+min(30,len(skill_result["matched"])*5)+(20 if location_ok else 0)+(20 if compensation_ok else 0)
    return {
        "role_match":role_match,"matched_skills":skill_result["matched"],"missing_skills":skill_result["missing"],
        "compensation_value_inr":compensation,"compensation_disclosed":compensation is not None,
        "compensation_ok":compensation_ok,"location_ok":location_ok,"score":score,
        "staff_experience_review_required":staff_review,
        "review_reasons":["Staff role explicitly requests more years than the verified profile."] if staff_review else [],
        "eligible":role_match and location_ok and compensation_ok and not staff_review,
    }
