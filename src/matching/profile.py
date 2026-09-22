from __future__ import annotations
import os

DEFAULT_SKILLS=["React","TypeScript","JavaScript","Next.js","Redux","Frontend Architecture","Frontend Performance","MQTT","Real-time systems","AI","Agentic engineering","Java","Spring Boot"]

def candidate_skills(profile: dict | None = None) -> list[str]:
    if profile and profile.get("skills"):
        return list(profile["skills"])
    raw=os.getenv("CANDIDATE_SKILLS")
    return [x.strip() for x in raw.split(",") if x.strip()] if raw else DEFAULT_SKILLS

def role_keywords(profile: dict | None = None) -> list[str]:
    if profile and profile.get("target_roles"):
        return [str(x).casefold() for x in profile["target_roles"] if str(x).strip()]
    raw=os.getenv("TARGET_ROLE_KEYWORDS","Senior Frontend,SDE III,Staff Frontend,Senior Full Stack,Senior Software Engineer,Lead Engineer")
    return [x.strip().casefold() for x in raw.split(",") if x.strip()]
