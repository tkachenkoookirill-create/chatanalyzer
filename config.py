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

# Report schedule (UTC times) — adjust for your timezone
# UTC+3 (Moscow/Kyiv): 9:00 → 06:00 UTC, 14:00 → 11:00 UTC, 19:00 → 16:00 UTC
SCHEDULE_TIMES_UTC = ["06:00", "11:00", "16:00"]

# How many hours back to look for messages each report window
LOOKBACK_HOURS = 5
