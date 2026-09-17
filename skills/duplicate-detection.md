# Duplicate Detection Skill

Prevent repeated discovery and application.

## Primary keys

1. Exact external job ID, when available.
2. Canonical application URL.
3. Normalized company + title + location.
4. Fuzzy title/company match when identifiers are missing.

Normalize:

- case
- whitespace
- tracking query parameters
- URL fragments
- common title variations

A job should be marked as duplicate when there is strong evidence that it represents the same opening.

When uncertain, flag for review instead of silently merging unrelated roles.
