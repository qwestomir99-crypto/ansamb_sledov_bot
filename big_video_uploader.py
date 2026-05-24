# ==========================================
# Файл: big_video_uploader.py
# Справка: README.md → Автопостинг / Большие видео
# Задача: отправка видео (>50 МБ) через пользовательский API (Telethon)
# Комментарий: требует TG_API_ID и TG_API_HASH из переменных окружения.
#              Работает через прокси (если задан PROXY_URL).
#              Функция send_big_video вызывается из bot.py и autoposter.py.
# Зависит от: telethon, os, asyncio
# Вызывается из: bot.py (команда /bigvideo), services/autoposter.py (после 1 июня)
# ==========================================
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import RPCError

API_ID = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH", "")
TARGET_CHAT_ID = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
PROXY_URL = os.environ.get("PROXY_URL")

def _parse_proxy(proxy_url: str):
    if not proxy_url:
        return None
    if proxy_url.startswith("socks5://"):
        without_proto = proxy_url[9:]
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
