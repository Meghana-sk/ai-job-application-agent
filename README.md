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

## Application history persistence

Application history is **not committed to this public repository**.

The daily workflow keeps the SQLite tracker on the GitHub Actions runner while it runs, then encrypts the database with AES-256-CBC + PBKDF2 and stores only the encrypted file as a GitHub Actions artifact named `application-history`. On the next run, the workflow retrieves the latest artifact and decrypts it before running the agent.

This design means the public repository contains no plaintext application history, resume data, contact information, or compensation target. The encryption key is stored only as the GitHub Actions repository secret `APPLICATION_HISTORY_KEY`.

The workflow uses a concurrency lock so two runs cannot update the same history at the same time.

### One-time setup

Generate a random key locally:

```bash
openssl rand -hex 32
```

Then add the generated value at:

**Repository → Settings → Secrets and variables → Actions → New repository secret**

Name:

```text
APPLICATION_HISTORY_KEY
```

Never commit or paste the key into the repository.

### Persistence limitation

Because this is a public repository, GitHub's artifact retention limit is currently up to 90 days. The workflow overwrites the named artifact on each successful run, refreshing its retention window. If the workflow does not run for longer than the retention period, the stored history can expire.

For long-term retention independent of GitHub Actions artifact retention, the next upgrade would be a dedicated private database/object store.

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
