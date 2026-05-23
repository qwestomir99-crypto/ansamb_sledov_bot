import asyncio
import os
from telethon import TelegramClient

# Временно любые значения
API_ID = 12345
API_HASH = "test"
SESSION_NAME = "temp_session"

async def main():
    print("🚀 Запуск получения ключей...")
    
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    
    real_api_id = client.api_id
    real_api_hash = client.api_hash
    
    print("\n" + "="*50)
    print("✅ ГОТОВЫЕ КЛЮЧИ:")
    print(f"TG_API_ID={real_api_id}")
    print(f"TG_API_HASH={real_api_hash}")
    print("="*50 + "\n")
    
    # Сохраняем в файл (если нужно)
    with open("tg_keys.env", "w") as f:
        f.write(f"TG_API_ID={real_api_id}\n")
        f.write(f"TG_API_HASH={real_api_hash}\n")
    
    print("📁 Ключи сохранены в файл: tg_keys.env")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
