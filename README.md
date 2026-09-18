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

## Current scope

This repository provides the search, matching, scoring, personalization, duplicate-detection, tracking, and safety architecture.

Actual job-board integrations should be added through APIs or authorized workflows. The agent must not bypass CAPTCHA, MFA, access controls, application safeguards, or site terms.

Application submission should remain approval-gated unless an authorized integration explicitly permits automated submission.

## Running locally

```bash
python -m src.main
```

Copy `.env.example` to `.env` for local configuration. Never commit `.env`.

## GitHub Actions

The included workflow runs the agent on a daily schedule. It currently executes the safe discovery pipeline and writes no personal data to the public repository.

Configure sensitive values as repository Actions Secrets before enabling production integrations.
