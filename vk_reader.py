import requests
import time
import os

# ---------- КОНФИГУРАЦИЯ ----------
VK_TOKEN = os.environ.get("VK_TOKEN")          # Токен доступа VK
OWNER_ID = 607754499                           # Твой числовой ID (из ссылки)
TG_BOT_TOKEN = os.environ.get("BOT_TOKEN")     # Токен твоего бота
TG_CHAT_ID = "@саперы_аутентичности"           # Канал для публикации

LAST_POST_FILE = "last_post.txt"

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
            post = data['response']['items'][0]
            return post
    except Exception as e:
        print(f"Ошибка при запросе к VK: {e}")
    return None

def send_to_telegram(post):
    """Отправляет пост в Telegram."""
    post_id = post['id']
    text = post.get('text', '')[:500]
    url = f"https://vk.com/wall{OWNER_ID}_{post_id}"
    message = f"📢 **Новый пост в VK**\n\n{text}\n\n🔗 [Читать дальше]({url})"
    
    # Отправляем через API бота
    api_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TG_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(api_url, json=payload)
        print(f"Пост {post_id} отправлен в Telegram")
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")

def main():
    print("VK Reader запущен. Проверяем новые посты...")
    last_id = get_last_post_id()
    while True:
        post = check_vk_wall()
        if post:
            post_id = post['id']
            if post_id > last_id:
                print(f"Новый пост {post_id}, отправляем...")
                send_to_telegram(post)
                save_last_post_id(post_id)
                last_id = post_id
            else:
                print(f"Новых постов нет (последний ID: {last_id})")
        else:
            print("Не удалось получить данные со стены VK")
        
        time.sleep(300)  # Проверяем раз в 5 минут

if __name__ == "__main__":
    main()
