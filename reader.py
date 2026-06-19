import os
import logging
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import User, Message
import config

log = logging.getLogger(__name__)

_session_str = os.getenv("SESSION_STRING", "").replace("\n", "").replace("\r", "").replace(" ", "").strip()
_session = StringSession(_session_str) if _session_str else "session"
client = TelegramClient(_session, config.API_ID, config.API_HASH)


async def start_client():
    """Connect once at startup and keep alive."""
    if not client.is_connected():
        log.info("Connecting Telethon client...")
        await client.connect()
        log.info("Telethon client connected.")


async def fetch_messages(group_identifier: str, hours_back: int) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    messages = []

    log.info(f"Getting entity for {group_identifier}...")
    entity = await client.get_entity(group_identifier)
    log.info(f"Got entity, fetching messages (limit=300)...")

    count = 0
    async for msg in client.iter_messages(entity, limit=300):
        count += 1
        if msg.date < since:
            break
        if not msg.text or not isinstance(msg, Message):
            continue

        sender_id = msg.sender_id
        username = None
        full_name = f"User_{sender_id}" if sender_id else "Неизвестно"

        if msg.sender and isinstance(msg.sender, User):
            username = f"@{msg.sender.username}" if msg.sender.username else None
            parts = [msg.sender.first_name or "", msg.sender.last_name or ""]
            full_name = " ".join(p for p in parts if p).strip() or full_name

        messages.append({
            "id": msg.id,
            "date": msg.date.strftime("%H:%M"),
            "text": msg.text[:300],
            "username": username,
            "full_name": full_name,
            "sender_id": sender_id,
        })

    log.info(f"Done: got {len(messages)} messages from {count} checked")
    messages.reverse()
    return messages


async def fetch_all_groups(hours_back: int) -> dict[str, list[dict]]:
    results = {}
    for group in config.MONITOR_GROUPS:
        try:
            msgs = await fetch_messages(group, hours_back)
            results[group] = msgs
        except Exception as e:
            log.error(f"Error fetching {group}: {e}")
            results[group] = {"error": str(e)}
    return results
