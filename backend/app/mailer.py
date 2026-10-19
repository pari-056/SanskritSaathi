from __future__ import annotations
import logging
import smtplib
from email.message import EmailMessage

from .config import get_settings

log = logging.getLogger("saathi.mail")


def send_email(to: str, subject: str, body: str) -> None:
    s = get_settings()
    if not s.smtp_host:
        # Development fallback: no SMTP configured, so print the message to the server log.
        log.warning("EMAIL (SMTP not configured) to=%s subject=%s\n%s", to, subject, body)
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = s.smtp_from, to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if s.smtp_user:
                smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)
    except Exception:
        log.exception("Failed to send email to %s", to)
