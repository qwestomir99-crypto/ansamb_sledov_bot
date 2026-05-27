#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from telethon import TelegramClient

DUMMY_API_ID = 12345
DUMMY_API_HASH = "dummy"
SESSION_NAME = "temp_session"

async def main():
    print("\n" + "=" * 50)
    print("🔑 Получение API_ID и API_HASH твоего аккаунта Telegram")
    print("=" * 50)
    
    phone = os.environ.get("TG_PHONE")
    if not phone:
        print("❌ Установи переменную TG_PHONE в GitHub Secrets")
        return
    
    client = TelegramClient(SESSION_NAME, DUMMY_API_ID, DUMMY_API_HASH)
    
    try:
        await client.start(phone=phone, code_callback=lambda: input("Введите код из Telegram: "))
        
        real_api_id = client.api_id
        real_api_hash = client.api_hash
        
        print("\n✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        print("\n🎯 ТВОИ КЛЮЧИ ДЛЯ RENDER:")
        print("=" * 50)
        print(f"TG_API_ID={real_api_id}")
        print(f"TG_API_HASH={real_api_hash}")
        print("=" * 50)
        
        with open("keys.txt", "w") as f:
            f.write(f"TG_API_ID={real_api_id}\n")
            f.write(f"TG_API_HASH={real_api_hash}\n")
        
        print("\n📁 Ключи также сохранены в файл: keys.txt")
        print("\n⚠️  ВАЖНО: Никому не показывай эти ключи!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        await client.disconnect()
        if os.path.exists(f"{SESSION_NAME}.session"):
            os.remove(f"{SESSION_NAME}.session")

if __name__ == "__main__":
    asyncio.run(main())
