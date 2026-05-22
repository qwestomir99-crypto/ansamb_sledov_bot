# ==========================================
# Файл: vk_reader.py
# Задача: чтение входящих сообщений из VK через Long Poll API и проброс в веб-морду
# Комментарий: подключается к VK Bots Long Poll, получает новые сообщения,
#              сохраняет их в очередь и отправляет через WebSocket в веб-морду.
#              Использует токен сообщества (не требует пользовательского токена).
# ==========================================

import requests
import time
import logging
import random
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

# Глобальная очередь сообщений и флаг активности
_message_queue = []
_websocket_broadcast = None
_active = True

def set_websocket_broadcast(callback):
    """Устанавливает функцию для отправки сообщений в веб-морду"""
    global _websocket_broadcast
    _websocket_broadcast = callback

def get_long_poll_server(vk_token: str, group_id: str) -> Optional[Dict]:
    """Получает параметры для подключения к Long Poll серверу"""
    url = "https://api.vk.com/method/groups.getLongPollServer"
    params = {
        "access_token": vk_token,
        "group_id": group_id,
        "v": "5.131"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "response" in data:
            return data["response"]
        else:
            logger.error(f"Ошибка получения Long Poll сервера: {data}")
            return None
    except Exception as e:
        logger.error(f"Исключение при получении Long Poll сервера: {e}")
        return None

def send_vk_message(vk_token: str, peer_id: int, text: str, attachment: str = None) -> bool:
    """Отправляет сообщение от имени сообщества"""
    url = "https://api.vk.com/method/messages.send"
    params = {
        "access_token": vk_token,
        "peer_id": peer_id,
        "message": text,
        "random_id": random.randint(1, 2**31),
        "v": "5.131"
    }
    if attachment:
        params["attachment"] = attachment
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "response" in data:
            logger.info(f"Сообщение отправлено в VK, peer_id={peer_id}")
            return True
        else:
            logger.error(f"Ошибка отправки сообщения: {data}")
            return False
    except Exception as e:
        logger.error(f"Исключение при отправке сообщения: {e}")
        return False

def listen_messages(vk_token: str, group_id: str, bot=None, chat_id=None):
    """Основной цикл получения сообщений из VK"""
    global _active
    
    logger.info("Запуск VK Long Poll слушателя")
    
    # Получаем параметры Long Poll
    lp_data = get_long_poll_server(vk_token, group_id)
    if not lp_data:
        logger.error("Не удалось получить Long Poll сервер")
        return
    
    server = lp_data["server"]
    key = lp_data["key"]
    ts = lp_data["ts"]
    
    logger.info(f"VK Long Poll подключён: server={server}")
    
    while _active:
        try:
            # Запрос к Long Poll серверу
            url = f"{server}?act=a_check&key={key}&ts={ts}&wait=25"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            # Обработка ошибок
            if "failed" in data:
                if data["failed"] == 1:
                    # Обновляем ts и продолжаем
                    ts = data.get("ts", ts)
                    logger.warning("VK Long Poll: обновлён ts")
                    continue
                elif data["failed"] == 2:
                    # Полное переподключение
                    logger.warning("VK Long Poll: переподключение")
                    lp_data = get_long_poll_server(vk_token, group_id)
                    if lp_data:
                        server = lp_data["server"]
                        key = lp_data["key"]
                        ts = lp_data["ts"]
                    continue
                elif data["failed"] == 3:
                    # Потерян ключ, переподключаемся
                    logger.warning("VK Long Poll: потерян ключ, переподключение")
                    lp_data = get_long_poll_server(vk_token, group_id)
                    if lp_data:
                        server = lp_data["server"]
                        key = lp_data["key"]
                        ts = lp_data["ts"]
                    continue
                else:
                    logger.error(f"VK Long Poll: неизвестная ошибка {data}")
                    time.sleep(5)
                    continue
            
            # Обновляем ts
            ts = data.get("ts", ts)
            
            # Обрабатываем обновления
            updates = data.get("updates", [])
            for update in updates:
                if update.get("type") == "message_new":
                    message_obj = update.get("object", {}).get("message", {})
                    if message_obj:
                        _process_new_message(message_obj, vk_token, bot, chat_id)
            
            # Небольшая пауза для снижения нагрузки
            time.sleep(0.2)
            
        except requests.exceptions.Timeout:
            logger.debug("VK Long Poll: таймаут, переподключение")
            continue
        except Exception as e:
            logger.error(f"VK Long Poll: исключение в цикле: {e}")
            time.sleep(5)
    
    logger.info("VK Long Poll слушатель остановлен")

def _process_new_message(message: Dict, vk_token: str, bot=None, chat_id=None):
    """Обрабатывает новое сообщение из VK"""
    try:
        from_id = message.get("from_id")
        peer_id = message.get("peer_id")
        text = message.get("text", "")
        date = message.get("date")
        
        # Пропускаем сообщения от самого бота (если есть такая проверка)
        # if from_id == vk_bot_id: return
        
        # Формируем объект сообщения
        msg_data = {
            "source": "vk",
            "from_id": from_id,
            "peer_id": peer_id,
            "text": text,
            "date": date,
            "timestamp": datetime.now().isoformat()
        }
        
        # Сохраняем в очередь
        _message_queue.append(msg_data)
        if len(_message_queue) > 1000:
            _message_queue.pop(0)
        
        # Отправляем в веб-морду через WebSocket
        if _websocket_broadcast:
            try:
                _websocket_broadcast(msg_data)
            except Exception as e:
                logger.error(f"Ошибка отправки в WebSocket: {e}")
        
        # Дублируем в Telegram, если задан chat_id
        if bot and chat_id:
            try:
                bot.send_message(
                    chat_id,
                    f"📩 *Новое сообщение из VK*\n"
                    f"От: {from_id}\n"
                    f"Текст: {text[:200]}",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления в Telegram: {e}")
        
        logger.info(f"VK сообщение от {from_id}: {text[:50]}...")
        
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения VK: {e}")

def get_message_queue() -> List[Dict]:
    """Возвращает очередь сообщений (для веб-морды)"""
    return _message_queue.copy()

def stop_listener():
    """Останавливает слушателя"""
    global _active
    _active = False

# Для обратной совместимости со старым кодом (vk_reader_loop)
def vk_reader_loop(bot, vk_token, vk_owner_id, chat_id):
    """Старая функция-обёртка для совместимости"""
    if vk_token and vk_owner_id:
        listen_messages(vk_token, vk_owner_id, bot, chat_id)
    else:
        logger.warning("VK токен или owner_id не заданы, слушатель не запущен")
