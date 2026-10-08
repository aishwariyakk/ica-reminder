"""
config.py — All user-configurable settings for the ICA Daily Reminder.
Edit this file to customise the reminder schedule, message, and AI provider.
"""

# ── Reminder schedule ──────────────────────────────────────────────────────── #

REMINDER_HOUR             = 15    # Start reminders from this hour (3 PM, 24-hour IST)
REMINDER_MINUTE           = 0     # Start minute within that hour
REMINDER_INTERVAL_MINUTES = 30    # Fire a notification every N minutes after start time
TIMEZONE                  = "Asia/Kolkata"   # IST (UTC+5:30)

# ── Desktop notification ───────────────────────────────────────────────────── #

NOTIFICATION_TITLE   = "ICA Daily Reminder"
NOTIFICATION_MESSAGE = (
    "Time to work on your ICA! Stay consistent — open your ICA task now."
)
NOTIFICATION_TIMEOUT = 60         # seconds the popup stays on screen (0 = never auto-close)

# ── IBM ICA (IBM Consulting Advantage) ────────────────────────────────────── #

ICA_URL = "https://canada.ica.ibm.com/ica/launchpad/"

# ── AI provider — IBM watsonx.ai (primary) ────────────────────────────────── #
# Get your API key at: https://cloud.ibm.com/iam/apikeys
# Get your Project ID from: https://dataplatform.cloud.ibm.com → project settings
#
# Supported model IDs (any watsonx.ai text-generation model):
#   ibm/granite-13b-instruct-v2      ← recommended (IBM-native, fast)
#   meta-llama/llama-3-1-70b-instruct
#   mistralai/mixtral-8x7b-instruct-v01

WATSONX_API_KEY    = ""           # e.g. "abc123..."
WATSONX_PROJECT_ID = ""           # e.g. "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
WATSONX_MODEL_ID   = "ibm/granite-13b-instruct-v2"
WATSONX_REGION     = "us-south"   # us-south | eu-de | jp-tok | au-syd

# ── AI provider — OpenAI (fallback) ───────────────────────────────────────── #
# Used automatically if WATSONX_API_KEY is not set.
# Get your key at: https://platform.openai.com/api-keys

OPENAI_API_KEY = ""               # e.g. "sk-..."
OPENAI_MODEL_ID = "gpt-4o-mini"   # gpt-4o-mini | gpt-4o | gpt-3.5-turbo

# ── Email notification (only used when --email flag is passed) ─────────────── #
# Gmail users: generate an App Password at
#   Google Account → Security → 2-Step Verification → App Passwords

EMAIL_SENDER   = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"   # Gmail App Password (not your real password)
EMAIL_RECEIVER = "your_email@gmail.com"
SMTP_HOST      = "smtp.gmail.com"
SMTP_PORT      = 587
