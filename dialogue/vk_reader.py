import time
import os
import json
import requests

CONFIG_FILE = "config.json"
LAST_POST_FILE = "last_post.txt"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        try:
            with open(LAST_POST_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, "w") as f:
        f.write(str(post_id))

def vk_reader_loop(bot, VK_TOKEN, OWNER_ID, TG_CHAT_ID):
    if not VK_TOKEN:
        print("VK Reader: VK_TOKEN не задан")
        return
    
    config = load_config()
    interval_seconds = config.get("vk_reader", {}).get("interval_seconds", 300)
    last_id = load_last_post_id()
    print(f"VK Reader: поток запущен, последний ID = {last_id}")
    
    while True:
        params = {
            'access_token': VK_TOKEN,
            'v': '5.131',
            'owner_id': OWNER_ID,
            'count': 1,
            'filter': 'owner'
        }
        try:
            response = requests.get('https://api.vk.com/method/wall.get', params=params, timeout=10)
            data = response.json()
            if 'response' in data and data['response']['items']:
                post = data['response']['items'][0]
                post_id = post['id']
                if post_id > last_id:
                    last_id = post_id
                    save_last_post_id(post_id)
                    text = post.get('text', '')[:500]
                    url = f"https://vk.com/wall{OWNER_ID}_{post_id}"
                    message = f"📢 **Новый пост в VK**\n\n{text}\n\n🔗 [Читать дальше]({url})"
                    bot.send_message(TG_CHAT_ID, message, parse_mode='Markdown')
                    print(f"VK Reader: отправлен пост {post_id}")
                else:
                    print(f"VK Reader: новых постов нет")
            else:
                print(f"VK Reader: ошибка API: {data}")
        except Exception as e:
            print(f"VK Reader ошибка: {e}")
        
        time.sleep(interval_seconds)
