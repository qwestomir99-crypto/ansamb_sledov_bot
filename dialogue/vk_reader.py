import time
import os
import requests

LAST_POST_FILE = "last_post.txt"

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

def check_vk_wall(bot, VK_TOKEN, OWNER_ID, TG_CHAT_ID):
    last_id = load_last_post_id()
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
                save_last_post_id(post_id)
                text = post.get('text', '')[:500]
                url = f"https://vk.com/wall{OWNER_ID}_{post_id}"
                message = f"📢 **Новый пост в VK**\n\n{text}\n\n🔗 [Читать дальше]({url})"
                bot.send_message(TG_CHAT_ID, message, parse_mode='Markdown')
                print(f"VK Reader: отправлен пост {post_id}")
            else:
                print(f"VK Reader: новых постов нет (последний ID {last_id})")
        else:
            print(f"VK Reader: ошибка API: {data}")
    except Exception as e:
        print(f"VK Reader ошибка: {e}")

def vk_reader_loop(bot, VK_TOKEN, OWNER_ID, TG_CHAT_ID):
    print("VK Reader: поток запущен")
    while True:
        if VK_TOKEN:
            check_vk_wall(bot, VK_TOKEN, OWNER_ID, TG_CHAT_ID)
        time.sleep(300)  # 5 минут
