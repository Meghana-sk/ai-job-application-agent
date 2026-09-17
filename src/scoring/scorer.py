def score_job(
    role_alignment: int,
    technical_alignment: int,
    location_alignment: int,
    seniority_alignment: int,
    compensation_evidence: int,
    source_freshness: int,
) -> int:
    components = [
        role_alignment,
        technical_alignment,
        location_alignment,
        seniority_alignment,
        compensation_evidence,
        source_freshness,
    ]

    if any(value < 0 for value in components):
        raise ValueError("Scores cannot be negative.")

    total = sum(components)
    if total > 100:
        raise ValueError("Score exceeds 100.")

    return total
