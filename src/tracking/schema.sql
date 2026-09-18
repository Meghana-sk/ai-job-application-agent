CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY,
    job_id TEXT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT,
    work_mode TEXT,
    application_url TEXT,
    source TEXT,
    discovered_at TIMESTAMPTZ NOT NULL,
    role_match BOOLEAN,
    matched_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    match_score DOUBLE PRECISION,
    compensation_value_inr BIGINT,
    compensation_currency TEXT,
    compensation_disclosed BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL,
    prepared_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    submission_reference TEXT,
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_updated_at TIMESTAMPTZ NOT NULL,
    duplicate_of TEXT,
    error_code TEXT,
    error_message TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_submitted_at ON applications(submitted_at);

CREATE TABLE IF NOT EXISTS application_events (
    event_id BIGSERIAL PRIMARY KEY,
    application_id TEXT NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_application_events_application_id
ON application_events(application_id);

CREATE INDEX IF NOT EXISTS idx_application_events_timestamp
ON application_events(timestamp);
