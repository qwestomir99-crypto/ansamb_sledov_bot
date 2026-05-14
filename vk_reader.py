import requests
import time
import os
from datetime import datetime

# ---------- КОНФИГУРАЦИЯ ----------
BOT_URL = "http://127.0.0.1:10000"           # Если скрипт на том же сервере
# BOT_URL = "https://ansamb-sledov6-bot.onrender.com"  # Если отдельно
TOKEN_SECRET = "tleem2026"                  # Секрет для доступа к /token
TG_CHAT_ID = "@саперы_аутентичности"         # Канал для публикации

VK_TOKEN = os.environ.get("VK_TOKEN")        # Токен доступа VK
OWNER_ID = 607754499                         # Твой числовой ID VK
LAST_POST_FILE = "last_post.txt"             # Файл с ID последнего поста

def get_bot_token():
    """Запрашивает токен у основного бота."""
    try:
        resp = requests.get(f"{BOT_URL}/token?secret={TOKEN_SECRET}")
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Ошибка получения токена: {resp.status_code}")
            return None
    except Exception as e:
        print(f"Не могу подключиться к боту: {e}")
        return None

def get_last_post_id():
    """Возвращает ID последнего обработанного поста из файла."""
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_last_post_id(post_id):
    """Сохраняет ID последнего поста в файл."""
    with open(LAST_POST_FILE, "w") as f:
        f.write(str(post_id))

def check_vk_wall():
    """Проверяет последний пост на стене VK."""
    if not VK_TOKEN:
        print("VK_TOKEN не задан в переменных окружения")
        return None
    
    params = {
        'access_token': VK_TOKEN,
        'v': '5.131',
        'owner_id': OWNER_ID,
        'count': 1,
        'filter': 'owner'
    }
    try:
        response = requests.get('https://api.vk.com/method/wall.get', params=params)
        data = response.json()
        if 'response' in data and data['response']['items']:
            return data['response']['items'][0]
        else:
            print(f"Ошибка VK API: {data}")
            return None
    except Exception as e:
        print(f"Ошибка при запросе к VK: {e}")
        return None

def send_to_telegram(post):
    """Отправляет пост в Telegram через основного бота."""
    token = get_bot_token()
    if not token:
        print("Нет токена, отправка невозможна")
        return False
    
    post_id = post['id']
    text = post.get('text', '')[:500]
    url = f"https://vk.com/wall{OWNER_ID}_{post_id}"
    message = f"📢 **Новый пост в VK**\n\n{text}\n\n🔗 [Читать дальше]({url})"
    
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': TG_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print(f"[{datetime.now()}] Пост {post_id} отправлен в Telegram")
            return True
        else:
            print(f"Ошибка {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False

def main():
    print("VK Reader запущен. Проверяю новые посты (раз в 5 минут)...")
    
    # Проверяем обязательные переменные
    if not VK_TOKEN:
        print("Ошибка: VK_TOKEN не задан. Добавь переменную окружения VK_TOKEN.")
        return
    
    # Проверяем доступность основного бота
    if not get_bot_token():
        print("Не удалось подключиться к основному боту. Завершение.")
        return
    
    last_id = get_last_post_id()
    print(f"Последний обработанный пост: {last_id}")
    
    while True:
        post = check_vk_wall()
        if post:
            post_id = post['id']
            if post_id > last_id:
                print(f"Новый пост {post_id}, отправляем...")
                if send_to_telegram(post):
                    save_last_post_id(post_id)
                    last_id = post_id
            else:
                print(f"Новых постов нет (последний ID: {last_id})")
        else:
            print("Не удалось получить данные со стены VK")
        
        time.sleep(300)  # Проверяем раз в 5 минут

if __name__ == "__main__":
    main()
