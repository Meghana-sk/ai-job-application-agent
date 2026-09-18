from enum import StrEnum


class ApplicationStatus(StrEnum):
    DISCOVERED = "discovered"
    MATCHED = "matched"
    PREPARED = "prepared"
    AWAITING_APPROVAL = "awaiting_approval"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    CLOSED = "closed"
    FAILED = "failed"
    SKIPPED = "skipped"
    DUPLICATE = "duplicate"
