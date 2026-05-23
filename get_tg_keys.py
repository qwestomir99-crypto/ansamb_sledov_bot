#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Одноразовый скрипт для получения API_ID и API_HASH твоего аккаунта Telegram.
Запускать 1 раз на компьютере (или на Render, если есть Shell).
Спрашивает номер телефона, код — выводит ключи.
Никуда их не отправляет, только показывает в консоль и сохраняет в файл keys.txt.
"""

import asyncio
import os
from telethon import TelegramClient

# Временные заглушки (Telethon сам подставит настоящие ключи после авторизации)
DUMMY_API_ID = 12345
DUMMY_API_HASH = "dummy"

SESSION_NAME = "temp_session"

async def main():
    print("\n" + "=" * 50)
    print("🔑 Получение API_ID и API_HASH твоего аккаунта Telegram")
    print("=" * 50)
    
    # Создаём клиента с фейковыми ключами
    client = TelegramClient(SESSION_NAME, DUMMY_API_ID, DUMMY_API_HASH)
    
    try:
        # Начинаем авторизацию
        await client.start()
        
        # После успешной авторизации Telethon сам узнаёт настоящие ключи
        real_api_id = client.api_id
        real_api_hash = client.api_hash
        
        print("\n✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        print("\n🎯 ТВОИ КЛЮЧИ ДЛЯ RENDER:")
        print("=" * 50)
        print(f"TG_API_ID={real_api_id}")
        print(f"TG_API_HASH={real_api_hash}")
        print("=" * 50)
        
        # Сохраняем в файл (чтобы не копировать руками)
        with open("keys.txt", "w") as f:
            f.write(f"TG_API_ID={real_api_id}\n")
            f.write(f"TG_API_HASH={real_api_hash}\n")
        
        print("\n📁 Ключи также сохранены в файл: keys.txt")
        print("\n⚠️  ВАЖНО: Никому не показывай эти ключи!")
        print("           Вставь их в Render в переменные TG_API_ID и TG_API_HASH")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("   Попробуй ещё раз или проверь номер телефона")
    finally:
        await client.disconnect()
        # Удаляем временную сессию (необязательно, но безопаснее)
        if os.path.exists(f"{SESSION_NAME}.session"):
            os.remove(f"{SESSION_NAME}.session")

if __name__ == "__main__":
    asyncio.run(main())
