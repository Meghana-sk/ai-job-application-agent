# AI Job Application Agent

An AI-assisted job discovery and application workflow for software engineering roles.

## What this project does

- Discovers relevant Senior Frontend / SDE III, Staff Frontend, and Senior Full Stack roles.
- Matches opportunities against a verified candidate profile.
- Uses transparent, configurable matching criteria.
- Generates truthful, tailored application material.
- Detects duplicate jobs and applications.
- Tracks application lifecycle and status history in a private local SQLite database.
- Supports a daily GitHub Actions workflow.
- Keeps sensitive candidate preferences outside the public repository.

## Privacy by design

Do **not** commit:

- Resume or CV
- Email, phone number, address, or other contact details
- Compensation targets
- Application history containing personal data
- API keys, cookies, session tokens, or credentials

Use GitHub Actions Secrets or a private local `.env` file for sensitive values.

The application tracker database is created under `data/`, which is gitignored.

## Project structure

```text
skills/                  Agent behavior specifications
config/                  Safe example configuration
src/                     Python implementation
  tracking/              Private application tracker schema/store
.github/workflows/       Scheduled workflow
.env.example             Environment variable template
.gitignore               Privacy and secret protection
```

## Application tracker

The tracker keeps one record per unique job opportunity and a separate status-event history.

### Core fields

- Job identity: `application_id`, `job_id`, `company`, `role`, `location`, `work_mode`, `application_url`, `source`
- Matching: `role_match`, `matched_skills`, `missing_skills`, `match_score`, compensation metadata
- Automation: `status`, `discovered_at`, `prepared_at`, `submitted_at`, `submission_reference`
- Deduplication: `first_seen_at`, `last_updated_at`, `duplicate_of`
- Failure: `error_code`, `error_message`
- Audit: `application_events`

### Status lifecycle

Typical lifecycle:

`discovered → matched → prepared → awaiting_approval → submitted`

Other supported states are `rejected`, `withdrawn`, `closed`, `failed`, `skipped`, and `duplicate`.

The tracker must never store passwords, cookies, auth tokens, CAPTCHA answers, MFA codes, payment information, or unnecessary personal data.

## Private PostgreSQL persistence

Application history is **not committed to this public repository**.

The daily workflow uses the Supabase PostgreSQL project as the persistent source of truth. The schema lives in `src/tracking/schema.sql`, with application records and status-event history.

The GitHub Actions runner receives the database connection only through the private `APPLICATION_DATABASE_URL` repository secret.

For GitHub Actions, use the Supabase **Session pooler** connection string on port 5432. Supabase documents the shared session pooler as the IPv4-compatible option for IPv4-only environments such as GitHub Actions.

### Required secrets

Add:

```text
APPLICATION_DATABASE_URL
MIN_COMPENSATION_INR
```

Optional controls:

```text
JOB_SEARCH_ENABLED
JOB_SEARCH_MAX_RESULTS
JOB_PROVIDER_BOARDS
CANDIDATE_SKILLS
```

The compensation threshold is intentionally not present anywhere in the public repository.

## Live ATS discovery

The agent now supports public Greenhouse and Lever job feeds.

Default provider boards are configured for several public ATS sites and can be overridden with `JOB_PROVIDER_BOARDS` as JSON:

```json
{"greenhouse":["monks"],"lever":["acceldata","hevodata","brillio-2","everbridge","weekdayworks"]}
```

The pipeline normalizes postings, filters for Bengaluru/Bangalore or remote roles, evaluates target seniority and technical alignment, and records the result in PostgreSQL.

## Application preparation and submission

The daily run now:

1. discovers live postings;
2. evaluates role, location, skills, and compensation;
3. records each opportunity;
4. prepares matched applications with the direct application URL;
5. marks prepared applications as `awaiting_approval`;
6. reports the run metrics.

It does **not** silently submit applications. Actual submission can require personal contact data, resume upload, employer-specific questions, authentication, CAPTCHA, MFA, or other safeguards. The agent must never bypass those controls.

A future authorized submission adapter can submit only when the required data and explicit approval are available.

## Running locally

```bash
python -m src.main
```

Copy `.env.example` to `.env` for local configuration. Never commit `.env`.

## GitHub Actions

The included workflow runs the agent on a daily schedule. It currently executes the safe discovery pipeline and writes no personal data to the public repository.

Configure sensitive values as repository Actions Secrets before enabling production integrations.
