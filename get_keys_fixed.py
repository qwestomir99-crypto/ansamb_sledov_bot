import asyncio
import os
from telethon import TelegramClient

# ВРЕМЕННЫЕ ЗАГЛУШКИ
API_ID = 12345
API_HASH = "test"

async def main():
    # Пробуем авторизоваться, Telethon сам подставит правильные ключи
    client = TelegramClient("session_fixed", API_ID, API_HASH)
    
    # ВАЖНО: перед запуском установи переменную окружения PHONE
    phone = os.environ.get("TG_PHONE")
    if not phone:
        print("❌ Установи переменную TG_PHONE в Render (твой номер телефона)")
        return
    
    await client.start(phone)
    print(f"✅ API_ID={client.api_id}")
    print(f"✅ API_HASH={client.api_hash}")

if __name__ == "__main__":
    asyncio.run(main())
