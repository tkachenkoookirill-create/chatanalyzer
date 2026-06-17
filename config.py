import os
from dotenv import load_dotenv

load_dotenv()

# Telegram user account (for reading groups)
API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")
PHONE = os.getenv("TG_PHONE", "")  # +79001234567

# Telegram bot (for sending reports)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
REPORT_CHAT_ID = int(os.getenv("REPORT_CHAT_ID", "0"))  # your personal chat id

# Claude API
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# Groups to monitor (usernames or numeric IDs, comma-separated)
# Example: "@sellers_wb,@ozon_sellers,-1001234567890"
MONITOR_GROUPS = [g.strip() for g in os.getenv("MONITOR_GROUPS", "").split(",") if g.strip()]

# Report schedule (UTC times) with lookback hours for each window
# Tashkent UTC+5: 11:00→06:00UTC (12h back), 16:00→11:00UTC (5h back), 21:00→16:00UTC (5h back)
SCHEDULE_WINDOWS = [
    {"utc_time": "04:00", "lookback_hours": 12, "label": "🌅 Утренний"},
    {"utc_time": "11:00", "lookback_hours": 5,  "label": "☀️ Дневной"},
    {"utc_time": "16:00", "lookback_hours": 5,  "label": "🌙 Вечерний"},
]
