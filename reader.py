from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.tl.types import User
import config

client = TelegramClient("session", config.API_ID, config.API_HASH)


async def fetch_messages(group_identifier: str, hours_back: int) -> list[dict]:
    """Fetch messages from a group for the last N hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    messages = []

    async with client:
        entity = await client.get_entity(group_identifier)
        async for msg in client.iter_messages(entity, limit=500):
            if msg.date < since:
                break
            if not msg.text:
                continue

            sender = await msg.get_sender()
            username = None
            full_name = "Неизвестно"

            if isinstance(sender, User):
                username = f"@{sender.username}" if sender.username else None
                parts = [sender.first_name or "", sender.last_name or ""]
                full_name = " ".join(p for p in parts if p).strip() or "Без имени"

            messages.append({
                "id": msg.id,
                "date": msg.date.strftime("%H:%M"),
                "text": msg.text,
                "username": username,
                "full_name": full_name,
                "sender_id": sender.id if sender else None,
            })

    # Reverse so oldest first
    messages.reverse()
    return messages


async def fetch_all_groups(hours_back: int) -> dict[str, list[dict]]:
    """Fetch messages from all configured groups."""
    results = {}
    for group in config.MONITOR_GROUPS:
        try:
            msgs = await fetch_messages(group, hours_back)
            results[group] = msgs
        except Exception as e:
            results[group] = {"error": str(e)}
    return results
