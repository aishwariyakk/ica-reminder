# 🤖 ICA Daily Reminder — AI-Powered IBM Consulting Coach

<div align="center">

![ICA Reminder Banner](https://img.shields.io/badge/ICA%20Reminder-AI%20Consulting%20Coach-1d4ed8?style=for-the-badge&logo=ibm&logoColor=white)

[![Built with IBM Bob](https://img.shields.io/badge/Built%20with-IBM%20Bob%20AI-0f62fe?style=flat-square&logo=ibm&logoColor=white)](https://www.ibm.com/products/bob)
[![AI Powered](https://img.shields.io/badge/AI-watsonx.ai%20%7C%20OpenAI-7c3aed?style=flat-square)](.)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-555?style=flat-square)](.)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776ab?style=flat-square&logo=python&logoColor=white)](.)
[![License](https://img.shields.io/badge/License-MIT-43e97b?style=flat-square)](LICENSE)

> **A desktop agent that fires a unique, AI-generated IBM Consulting Advantage task every 30 minutes.**  
> Powered by IBM watsonx.ai (or OpenAI as fallback). Zero extra dependencies.

</div>

---

## 🤖 Built with AI — IBM Bob

This project was **designed, architected, and built end-to-end using [IBM Bob](https://www.ibm.com/products/bob)**, IBM's AI software engineering assistant.

### How AI was used in this project

| Phase | AI Contribution |
|---|---|
| **Architecture** | Bob designed the subprocess-based popup isolation pattern (tkinter always on main thread) |
| **Task generation** | Bob built `ai_task.py` — the watsonx.ai + OpenAI dual-provider LLM client using only Python stdlib (`urllib`) |
| **Prompt engineering** | Bob authored the system prompt and dynamic user prompt that vary by day, time, and randomly selected focus area |
| **Scheduler logic** | Bob implemented the IST-aware polling loop with per-slot firing guard |
| **Notification UX** | Bob designed the tkinter popup with countdown timer, scrollable task text, and bottom-right screen positioning |
| **Email integration** | Bob wrote the dual-format (plain + HTML) SMTP notification with HTML styling |
| **Cross-platform support** | Bob added Windows/macOS/Linux startup instructions and the VBScript silent launcher |
| **Documentation** | Bob authored this README and all inline docstrings |

> 💡 **What makes this different:** Instead of cycling through a fixed list of tasks, this agent calls a live LLM (IBM watsonx.ai Granite or OpenAI GPT) on every reminder. The LLM knows today's date and day-of-week, picks a random consulting focus area, and generates a unique, contextual task you have never seen before.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🧠 **AI-generated tasks** | Every reminder fires a unique task from IBM watsonx.ai (Granite) or OpenAI — never repeats |
| 📅 **Context-aware prompts** | The LLM receives today's date, day-of-week, and a random focus area for truly varied output |
| 🔄 **Provider fallback chain** | watsonx.ai → OpenAI → static fallback — works even offline |
| ⏰ **IST-aware scheduler** | Polling loop fires at 3:00 PM IST, then every 30 minutes — accurate to ±30 seconds |
| 🖥️ **Native desktop popup** | Tkinter window in the bottom-right corner with countdown, scrollable task, and "Open ICA" button |
| 📧 **Email notifications** | Optional dual-format (plain + HTML) email via Gmail SMTP (`--email` flag) |
| 🪟 **Silent Windows startup** | VBScript launcher hides the console window at login |
| 🐧 **Cross-platform** | Windows (Task Scheduler / VBS) · macOS (launchd) · Linux (cron / systemd) |
| 📝 **Structured logging** | Timestamped log for every scheduler tick and notification attempt |
| 🔌 **Zero extra dependencies** | AI calls use Python's built-in `urllib` — only `plyer` and `pytz` needed |

---

## 🏗️ Architecture

```
Windows Task Scheduler / launchd / cron
    └── start_reminder.vbs (silent)
            └── python -m ica_reminder.reminder
                    │
                    ├── run_scheduler()          ← IST polling loop (every 30 s)
                    │       └── reminder_job()   ← fires when slot triggers
                    │               │
                    │               ├── generate_task()          ← ai_task.py
                    │               │       ├── _call_watsonx()  ← IBM watsonx.ai
                    │               │       ├── _call_openai()   ← OpenAI (fallback)
                    │               │       └── _FALLBACK        ← static (offline)
                    │               │
                    │               ├── send_desktop_notification()
                    │               │       └── subprocess: popup.py  ← tkinter window
                    │               │
                    │               └── send_email_notification()  (--email only)
                    │
                    └── Logs to stdout  (timestamped)
```

**Key design choices:**
- `popup.py` runs as a **separate subprocess** so tkinter always executes on its own main thread — avoids deadlocks when called from a scheduler loop.
- Task text is passed via a **temp file** (not stdin/pipe) to eliminate pipe buffering issues on Windows.
- `CREATE_NO_WINDOW` flag suppresses the console flash on Windows when launching the subprocess.
- The LLM prompt injects `datetime.now(IST)` and a randomly selected focus area — every call produces genuinely different output.
- All HTTP calls use Python's built-in `urllib` — no `requests` or `httpx` needed.

---

## 📁 File Structure

```
ica_reminder/
├── ica_reminder/
│   ├── __init__.py        ← Package marker
│   ├── config.py          ← All settings: schedule, AI keys, email
│   ├── ai_task.py         ← AI task generator (watsonx.ai + OpenAI + fallback)
│   ├── reminder.py        ← Scheduler + notification orchestrator
│   └── popup.py           ← Tkinter desktop popup (runs as subprocess)
├── requirements.txt       ← plyer, pytz (only 2 dependencies)
├── pyproject.toml         ← Package metadata + entry point
├── setup_task_scheduler.ps1  ← Windows Task Scheduler registration
├── start_reminder.vbs     ← Silent Windows launcher (no console window)
└── README.md              ← This file
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
# or
pip install plyer pytz
```

### 2. Configure your AI provider

Open [`ica_reminder/config.py`](ica_reminder/config.py) and set **one** of:

**Option A — IBM watsonx.ai (recommended for IBM employees)**
```python
WATSONX_API_KEY    = "your-ibm-cloud-api-key"
WATSONX_PROJECT_ID = "your-watsonx-project-id"
WATSONX_MODEL_ID   = "ibm/granite-13b-instruct-v2"   # or any watsonx model
WATSONX_REGION     = "us-south"
```
Get your API key: [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)  
Get your Project ID: [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → project settings

**Option B — OpenAI (fallback)**
```python
OPENAI_API_KEY  = "sk-..."
OPENAI_MODEL_ID = "gpt-4o-mini"
```

**Option C — No API key (offline mode)**  
Leave both blank. A clear, well-structured static task is shown instead.

### 3. Run

```bash
# Desktop notification only
python -m ica_reminder.reminder

# Desktop + email
python -m ica_reminder.reminder --email

# Test immediately (fires one notification and exits)
python -m ica_reminder.reminder --test
```

---

## ⏰ Run on Startup

### Windows — Task Scheduler (recommended, silent)

```powershell
# Run as Administrator
.\setup_task_scheduler.ps1
```

Or use the silent VBScript launcher manually:
```
start_reminder.vbs   ← double-click to start with no console window
```

### macOS — launchd

```bash
# Create ~/Library/LaunchAgents/com.ica.reminder.plist pointing to the script
launchctl load ~/Library/LaunchAgents/com.ica.reminder.plist
```

### Linux — crontab

```bash
@reboot /usr/bin/python3 -m ica_reminder.reminder &
```

---

## 🤖 How the AI Task Generation Works

Every time a reminder fires, [`ai_task.py`](ica_reminder/ai_task.py) runs this pipeline:

1. **Picks a random focus area** from 15 consulting categories (e.g. "client communication", "risk identification", "prompt engineering for consulting tasks")
2. **Builds a contextual prompt** including today's date and day-of-week in IST
3. **Calls the LLM** with a consultant productivity coach system prompt
4. **Returns a structured task** in this format:
   ```
   TASK: <one-line title>

   WHY TODAY: <one sentence on relevance>

   STEPS:
     1. ...
     2. ...
     3. ...

   TIP: <practical tip>
   ```

Focus areas include:
- AI-assisted document drafting · meeting notes and action items
- Client communication · knowledge sharing · prompt engineering
- Project status reporting · risk identification · workshop facilitation
- Learning a new ICA feature · automating repetitive consulting tasks
- Stakeholder updates · lessons-learned documentation · and more

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| AI (primary) | IBM watsonx.ai — `ibm/granite-13b-instruct-v2` via REST API |
| AI (fallback) | OpenAI Chat Completions API |
| HTTP | Python stdlib `urllib` — zero extra dependencies |
| Desktop UI | `tkinter` (Python built-in) |
| Notifications | `plyer` cross-platform wrapper |
| Timezone | `pytz` — IST-aware scheduling |
| Startup | Windows Task Scheduler / VBScript · macOS launchd · Linux cron |
| AI Tooling | IBM Bob (design, code generation, debugging, documentation) |

---

## 📋 Requirements

- Python 3.8 or later
- Windows 10/11 · macOS · Linux
- `pip install plyer pytz`
- IBM Cloud API key (for watsonx.ai) **or** OpenAI API key **or** neither (offline fallback)
- No internet required in offline fallback mode

---

## 🔧 Troubleshooting

### Popup not appearing

```bash
# Test directly
python -m ica_reminder.reminder --test
```

### watsonx.ai returning 401

- Check your API key at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
- Verify your `WATSONX_PROJECT_ID` in the watsonx.ai project settings
- Ensure your IBM Cloud account has watsonx.ai provisioned in the selected region

### Scheduler not firing on Windows

```powershell
Get-ScheduledTask -TaskName "ICA_Reminder" | Get-ScheduledTaskInfo
```

---

## 📄 License

MIT © 2025 — see [LICENSE](LICENSE)

---

<div align="center">

**ICA Daily Reminder** — Built with [IBM Bob AI](https://www.ibm.com/products/bob)  
Powered by IBM watsonx.ai · Python · tkinter · Zero extra dependencies

*A demonstration of AI-assisted agent engineering for real daily IBM consulting workflows.*

</div>
