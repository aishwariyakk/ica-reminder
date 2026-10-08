"""
ai_task.py — Generates a unique, contextual ICA task suggestion using an LLM.

Provider priority:
  1. IBM watsonx.ai   (set WATSONX_API_KEY + WATSONX_PROJECT_ID in config.py)
  2. OpenAI           (set OPENAI_API_KEY in config.py)
  3. Static fallback  (returns a hardcoded prompt if no API key is configured)

The prompt is deliberately varied by injecting the current date, day-of-week,
and a random seed so every call produces a meaningfully different task.
"""

import json
import logging
import random
import urllib.request
import urllib.error
from datetime import datetime

import pytz

from ica_reminder.config import (
    TIMEZONE,
    ICA_URL,
    WATSONX_API_KEY,
    WATSONX_PROJECT_ID,
    WATSONX_MODEL_ID,
    WATSONX_REGION,
    OPENAI_API_KEY,
    OPENAI_MODEL_ID,
)

log = logging.getLogger(__name__)

# ── Prompt template ────────────────────────────────────────────────────────── #

_SYSTEM_PROMPT = (
    "You are an IBM consulting productivity coach. "
    "Your job is to suggest one specific, actionable ICA (IBM Consulting Advantage) task "
    "that an IBM consultant should complete today. "
    "ICA is IBM's AI-powered platform for consultants, available at " + ICA_URL + ". "
    "Keep the task concrete and achievable in 15-30 minutes. "
    "Format your response as:\n"
    "TASK: <one-line task title>\n\n"
    "WHY TODAY: <one sentence on why this is valuable right now>\n\n"
    "STEPS:\n"
    "  1. <step>\n"
    "  2. <step>\n"
    "  3. <step>\n"
    "  (3-5 steps total)\n\n"
    "TIP: <one practical tip to get the most out of this task>"
)

_FOCUS_AREAS = [
    "AI-assisted document drafting",
    "meeting notes and action items",
    "client communication",
    "knowledge sharing with the team",
    "prompt engineering for consulting tasks",
    "project status reporting",
    "risk identification and mitigation",
    "workshop facilitation preparation",
    "learning a new ICA feature",
    "automating a repetitive consulting task",
    "stakeholder update preparation",
    "lessons-learned documentation",
    "onboarding a colleague to ICA",
    "code or script generation for data tasks",
    "using ICA's Document Intelligence on a long PDF",
]


def _build_user_prompt(now_ist: datetime) -> str:
    focus = random.choice(_FOCUS_AREAS)
    return (
        f"Today is {now_ist.strftime('%A, %d %B %Y')} (IST). "
        f"Suggest one ICA task focused on: {focus}. "
        "Make it specific to what a consultant would realistically do today."
    )


# ── watsonx.ai provider ────────────────────────────────────────────────────── #

def _get_watsonx_token(api_key: str, region: str) -> str:
    """Exchange an IBM Cloud API key for a short-lived IAM bearer token."""
    url = "https://iam.cloud.ibm.com/identity/token"
    body = f"grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey={api_key}"
    req = urllib.request.Request(url, data=body.encode(), method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["access_token"]


def _call_watsonx(user_prompt: str) -> str:
    token = _get_watsonx_token(WATSONX_API_KEY, WATSONX_REGION)
    url = (
        f"https://{WATSONX_REGION}.ml.cloud.ibm.com"
        "/ml/v1/text/generation?version=2024-03-19"
    )
    payload = {
        "model_id": WATSONX_MODEL_ID,
        "project_id": WATSONX_PROJECT_ID,
        "input": f"<|system|>\n{_SYSTEM_PROMPT}\n<|user|>\n{user_prompt}\n<|assistant|>\n",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 400,
            "repetition_penalty": 1.1,
        },
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["results"][0]["generated_text"].strip()


# ── OpenAI provider ────────────────────────────────────────────────────────── #

def _call_openai(user_prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": OPENAI_MODEL_ID,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.85,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {OPENAI_API_KEY}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


# ── Static fallback ────────────────────────────────────────────────────────── #

_FALLBACK = (
    "TASK: Draft an executive summary using ICA's AI Assistant\n\n"
    "WHY TODAY: Practising with ICA's AI tools daily builds speed and confidence.\n\n"
    "STEPS:\n"
    "  1. Open ICA: " + ICA_URL + "\n"
    "  2. Click 'AI Assistant' from the Launchpad.\n"
    "  3. Paste a prompt describing your current project and ask for a 1-page summary.\n"
    "  4. Edit the output to match your project specifics.\n"
    "  5. Save it to your project notes.\n\n"
    "TIP: Add '[CONFIGURE AI]' to your task list — set WATSONX_API_KEY or "
    "OPENAI_API_KEY in config.py to get unique AI-generated tasks every reminder."
)


# ── Public API ─────────────────────────────────────────────────────────────── #

def generate_task() -> str:
    """
    Return a unique ICA task string.
    Tries watsonx.ai first, then OpenAI, then falls back to a static task.
    """
    ist = pytz.timezone(TIMEZONE)
    now_ist = datetime.now(ist)
    user_prompt = _build_user_prompt(now_ist)

    if WATSONX_API_KEY and WATSONX_PROJECT_ID:
        try:
            log.info("Generating task via IBM watsonx.ai...")
            task = _call_watsonx(user_prompt)
            log.info("watsonx.ai task generated successfully.")
            return task
        except Exception as exc:
            log.warning("watsonx.ai call failed (%s); trying OpenAI...", exc)

    if OPENAI_API_KEY:
        try:
            log.info("Generating task via OpenAI...")
            task = _call_openai(user_prompt)
            log.info("OpenAI task generated successfully.")
            return task
        except Exception as exc:
            log.warning("OpenAI call failed (%s); using static fallback.", exc)

    log.info("No AI provider configured — using static fallback task.")
    return _FALLBACK
