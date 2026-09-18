CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY,
    job_id TEXT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT,
    work_mode TEXT,
    application_url TEXT,
    source TEXT,
    discovered_at TEXT NOT NULL,
    role_match INTEGER,
    matched_skills TEXT,
    missing_skills TEXT,
    match_score REAL,
    compensation_value_inr INTEGER,
    compensation_currency TEXT,
    compensation_disclosed INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    prepared_at TEXT,
    submitted_at TEXT,
    submission_reference TEXT,
    first_seen_at TEXT NOT NULL,
    last_updated_at TEXT NOT NULL,
    duplicate_of TEXT,
    error_code TEXT,
    error_message TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_submitted_at ON applications(submitted_at);

CREATE TABLE IF NOT EXISTS application_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT,
    FOREIGN KEY(application_id) REFERENCES applications(application_id)
);

CREATE INDEX IF NOT EXISTS idx_application_events_application_id
ON application_events(application_id);
