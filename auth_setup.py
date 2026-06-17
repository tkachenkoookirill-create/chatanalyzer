"""
Run this ONCE locally to authorize your Telegram account.
This creates a 'session' file that Railway will use.

Usage: python auth_setup.py
"""
import asyncio
from telethon import TelegramClient
import config

async def main():
    async with TelegramClient("session", config.API_ID, config.API_HASH) as client:
        await client.start(phone=config.PHONE)
        me = await client.get_me()
        print(f"✅ Авторизован как: {me.first_name} (@{me.username})")
        print("Файл 'session.session' создан. Загрузи его в Railway.")

if __name__ == "__main__":
    asyncio.run(main())
