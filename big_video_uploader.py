import os
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError

# Переменные окружения (заполни в Render)
API_ID = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH", "")
TARGET_CHAT_ID = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
PROXY_URL = os.environ.get("PROXY_URL")  # если есть, формат: socks5://логин:пароль@ip:port

def _parse_proxy(proxy_url: str):
    """Преобразует PROXY_URL в формат Telethon"""
    if not proxy_url:
        return None
    
    # Простейший парсер для socks5://login:pass@ip:port
    if proxy_url.startswith("socks5://"):
        without_proto = proxy_url[9:]  # убираем socks5://
        if "@" in without_proto:
            auth, addr = without_proto.split("@")
            login, password = auth.split(":", 1)
            host, port = addr.split(":")
            return {
                "proxy_type": "socks5",
                "addr": host,
                "port": int(port),
                "username": login,
                "password": password
            }
        else:
            host, port = without_proto.split(":")
            return {
                "proxy_type": "socks5",
                "addr": host,
                "port": int(port)
            }
    return None

async def send_big_video(file_path: str, caption: str = ""):
    """
    Отправляет большое видео (до 2 ГБ) через пользовательский API.
    Возвращает True при успехе, False при ошибке.
    """
    if not API_ID or not API_HASH:
        print("[BIG_VIDEO] Ошибка: TG_API_ID или TG_API_HASH не заданы")
        return False
    
    if not os.path.exists(file_path):
        print(f"[BIG_VIDEO] Ошибка: файл {file_path} не найден")
        return False
    
    proxy = _parse_proxy(PROXY_URL)
    client = TelegramClient("user_session", API_ID, API_HASH, proxy=proxy)
    
    try:
        await client.start()
        # Отправляем файл (Telethon сам определит тип)
        await client.send_file(TARGET_CHAT_ID, file_path, caption=caption)
        print(f"[BIG_VIDEO] Файл {file_path} отправлен в {TARGET_CHAT_ID}")
        return True
    except RPCError as e:
        print(f"[BIG_VIDEO] RPC ошибка: {e}")
        return False
    except Exception as e:
        print(f"[BIG_VIDEO] Ошибка: {e}")
        return False
    finally:
        await client.disconnect()

# Для тестирования локально
if __name__ == "__main__":
    async def test():
        await send_big_video("test.mp4", "Тестовое видео")
    
    asyncio.run(test())
