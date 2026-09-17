# Job Search Skill

## Objective

Find new opportunities that match the configured role, location, work-mode, compensation, and technical-skill preferences.

## Rules

1. Prefer authoritative job postings and direct application pages.
2. Prefer newly discovered roles over stale listings.
3. Deduplicate by canonical application URL, job ID, and normalized company/title/location.
4. Do not infer compensation when it is not published.
5. Treat missing compensation as unknown, not as failure.
6. Do not fabricate remote/hybrid status.
7. Preserve the source URL for every discovered role.
8. Do not collect unnecessary personal information.
9. Never bypass CAPTCHA, MFA, authentication barriers, robots controls, or other access restrictions.

## Output

For each opportunity:

- company
- role
- location
- work mode
- compensation, if explicitly available
- source
- direct application URL
- match summary
