from __future__ import annotations
"""Human-approved browser submission safeguards.

Never bypass CAPTCHA/MFA or collect passwords. Interactive challenges pause the
submission and require the user to complete them.
"""
from dataclasses import dataclass
from enum import StrEnum
import time

class BlockReason(StrEnum):
    LOGIN_REQUIRED="login_required"
    CAPTCHA_REQUIRED="captcha_required"
    MFA_REQUIRED="mfa_required"
    FILE_UPLOAD_REQUIRED="file_upload_required"
    UNSUPPORTED_FORM="unsupported_form"
    FAILED_SUBMISSION="failed_submission"
    APPROVAL_REQUIRED="approval_required"

@dataclass
class SubmissionResult:
    status: str
    reason: str|None=None
    reference: str|None=None
    attempts: int=0

def validate_submission_context(app: dict) -> None:
    if app.get("status") != "approved" or not app.get("approved_at"):
        raise RuntimeError(BlockReason.APPROVAL_REQUIRED.value)

def classify_browser_interruption(*, login=False, captcha=False, mfa=False, file_upload=False, unsupported=False):
    if captcha: return BlockReason.CAPTCHA_REQUIRED.value
    if mfa: return BlockReason.MFA_REQUIRED.value
    if login: return BlockReason.LOGIN_REQUIRED.value
    if file_upload: return BlockReason.FILE_UPLOAD_REQUIRED.value
    if unsupported: return BlockReason.UNSUPPORTED_FORM.value
    return None

def submit_approved_application(app: dict, browser, max_attempts: int=2) -> SubmissionResult:
    validate_submission_context(app)
    attempts=0
    browser.open(app["application_url"])

    for _ in range(max_attempts):
        attempts += 1
        interruption=classify_browser_interruption(
            login=browser.detect_login(),
            captcha=browser.detect_captcha(),
            mfa=browser.detect_mfa(),
            file_upload=browser.detect_file_upload(),
        )
        if interruption:
            return SubmissionResult("blocked", interruption, attempts=attempts)

        try:
            browser.fill_supported_fields(app.get("form_fields", {}))
            browser.click("submit")
            if browser.detect_success():
                return SubmissionResult("submitted", reference=browser.submission_reference(), attempts=attempts)
        except Exception:
            time.sleep(2)

    return SubmissionResult("failed", BlockReason.FAILED_SUBMISSION.value, attempts=attempts)
