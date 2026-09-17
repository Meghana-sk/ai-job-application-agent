def match_skills(
    required_skills: list[str],
    candidate_skills: list[str],
) -> dict[str, list[str]]:
    candidate = {skill.casefold() for skill in candidate_skills}

    matched = [skill for skill in required_skills if skill.casefold() in candidate]
    missing = [skill for skill in required_skills if skill.casefold() not in candidate]

    return {"matched": matched, "missing": missing}
