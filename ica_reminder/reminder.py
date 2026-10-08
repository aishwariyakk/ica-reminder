"""
reminder.py — Core scheduler and notification logic.
Imports all settings from config.py.

Usage:
    python -m ica_reminder.reminder             # desktop notification only
    python -m ica_reminder.reminder --email     # desktop + email notification
"""

import sys
import time
import argparse
import smtplib
import logging
import tempfile
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

import pytz

from ica_reminder.config import (
    REMINDER_HOUR,
    REMINDER_MINUTE,
    REMINDER_INTERVAL_MINUTES,
    TIMEZONE,
    NOTIFICATION_TITLE,
    NOTIFICATION_MESSAGE,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER,
    SMTP_HOST,
    SMTP_PORT,
    ICA_URL,
)
from ica_reminder.ai_task import generate_task

# ──────────────────────────────────────────────────────────────────────────── #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Notification senders ───────────────────────────────────────────────────── #

def send_desktop_notification(task: str) -> None:
    """Write the task to a temp file and launch popup.py as a detached process.

    Passing via file instead of stdin avoids all pipe/deadlock issues.
    CREATE_NO_WINDOW suppresses the console flash on Windows.
    Popen returns immediately — the popup runs independently.
    """
    # Write task text to a temp file; popup.py reads and deletes it
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    tmp.write(task)
    tmp.close()

    # CREATE_NO_WINDOW — Windows flag, no console window flashes up
    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen(
        [sys.executable, "-m", "ica_reminder.popup", tmp.name],
        creationflags=CREATE_NO_WINDOW,
    )
    log.info("Desktop popup launched.")


def send_email_notification(task: str) -> None:
    """Send a reminder email via SMTP (Gmail by default)."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = NOTIFICATION_TITLE
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER

        plain_body = (
            "Hi,\n\n"
            "This is your daily ICA reminder.\n\n"
            f"{NOTIFICATION_MESSAGE}\n\n"
            f"Today's suggested ICA task:\n{task}\n\n"
            f"Open IBM Consulting Advantage: {ICA_URL}\n\n"
            "Keep up the great work!\n"
        )
        html_body = f"""\
<html>
  <body style="font-family:sans-serif;padding:20px">
    <h2 style="color:#3b82d4">ICA Daily Reminder</h2>
    <p style="font-size:15px">{NOTIFICATION_MESSAGE}</p>
    <table style="border-left:4px solid #3b82d4;padding:10px 16px;background:#f7f8fa;margin:16px 0">
      <tr><td>
        <p style="margin:0 0 6px 0;font-weight:600;font-size:14px">Today's suggested ICA task</p>
        <p style="margin:0;font-size:14px">{task}</p>
      </td></tr>
    </table>
    <p style="font-size:14px">
      <a href="{ICA_URL}" style="color:#3b82d4">Open IBM Consulting Advantage &rarr;</a>
    </p>
    <p style="color:#57606a;font-size:13px">Sent automatically at 3:00 PM IST.</p>
  </body>
</html>"""

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body,  "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        log.info("Email notification sent to %s.", EMAIL_RECEIVER)
    except Exception as exc:
        log.error("Email notification failed: %s", exc)


# ── Core job ───────────────────────────────────────────────────────────────── #

def reminder_job(send_email: bool = False, now_ist: Optional[datetime] = None) -> None:
    """Fires all enabled notifications."""
    ist = pytz.timezone(TIMEZONE)
    if now_ist is None:
        now_ist = datetime.now(ist)
    log.info("Reminder fired at %s IST", now_ist.strftime("%Y-%m-%d %H:%M:%S"))
    task = generate_task()
    log.info("ICA task generated.")
    send_desktop_notification(task)
    if send_email:
        send_email_notification(task)


# ── Scheduler ─────────────────────────────────────────────────────────────── #

def run_scheduler(send_email: bool) -> None:
    """
    IST-aware polling loop.

    Fires once at REMINDER_HOUR:REMINDER_MINUTE, then repeats every
    REMINDER_INTERVAL_MINUTES.  A (slot_key) guard ensures each slot
    fires exactly once even if the loop wakes up multiple times within it.
    """
    ist              = pytz.timezone(TIMEZONE)
    last_fired_slot  = None   # "YYYY-MM-DD HH:MM" of the last fired slot

    log.info(
        "ICA reminder: first fire at %02d:%02d IST, then every %d minutes.  "
        "Press Ctrl+C to stop.",
        REMINDER_HOUR,
        REMINDER_MINUTE,
        REMINDER_INTERVAL_MINUTES,
    )

    while True:
        now_ist  = datetime.now(ist)
        # Total minutes elapsed since midnight IST
        mins_since_midnight = now_ist.hour * 60 + now_ist.minute
        start_mins          = REMINDER_HOUR * 60 + REMINDER_MINUTE

        # Has the start time been reached today?
        if mins_since_midnight >= start_mins:
            # Which interval slot are we in?
            elapsed   = mins_since_midnight - start_mins
            slot_num  = elapsed // REMINDER_INTERVAL_MINUTES
            slot_key  = f"{now_ist.date()} {slot_num}"

            if slot_key != last_fired_slot:
                reminder_job(send_email=send_email, now_ist=now_ist)
                last_fired_slot = slot_key

        time.sleep(30)   # poll every 30 s  (±30 s accuracy)


# ── Entry point ────────────────────────────────────────────────────────────── #

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            f"ICA Reminder — fires at {REMINDER_HOUR:02d}:{REMINDER_MINUTE:02d} IST "
            f"then every {REMINDER_INTERVAL_MINUTES} minutes."
        )
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Also send an email notification (configure config.py first).",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Fire the notification immediately (for testing) then exit.",
    )
    args = parser.parse_args()
    if args.test:
        log.info("--- TEST MODE: firing notification now ---")
        reminder_job(send_email=args.email)
        log.info("--- TEST MODE: done ---")
    else:
        run_scheduler(send_email=args.email)


if __name__ == "__main__":
    main()
