import os
import asyncio
from telethon import TelegramClient, events

# Конфигурация (взять из переменных окружения Render)
API_ID = int(os.environ.get("TG_API_ID"))
API_HASH = os.environ.get("TG_API_HASH")
PHONE_NUMBER = os.environ.get("TG_PHONE_NUMBER")
ALISA_BOT = "@alisa"

client = TelegramClient('userbot_session', API_ID, API_HASH)

async def ask_alisa_async(prompt: str, timeout: int = 30) -> str | None:
    """Отправляет сообщение @alisa и ждёт ответа."""
    try:
        # Отправляем сообщение Алисе
        await client.send_message(ALISA_BOT, prompt)

        # Ждём ответ (событие)
        @client.on(events.NewMessage(chats=ALISA_BOT))
        async def handler(event):
            if event.message.text and not event.out:
                # Получили ответ — отключаем обработчик и возвращаем текст
                client.remove_event_handler(handler)
                return event.message.text

        # Запускаем клиент, если ещё не запущен
        if not client.is_connected():
            await client.start(phone=PHONE_NUMBER)

        # Ждём ответ с таймаутом
        async with client:
            try:
                response = await asyncio.wait_for(handler, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                return None
    except Exception as e:
        print(f"[AlisaClient] Ошибка: {e}")
        return None

def ask_alisa(prompt: str) -> str | None:
    """Синхронная обёртка для вызова из bot.py"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(ask_alisa_async(prompt))
