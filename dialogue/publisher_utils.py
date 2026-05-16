import requests

def post_to_telegram(bot, chat_id, message):
    try:
        bot.send_message(chat_id, message, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"Ошибка Telegram: {e}")
        return False

def post_to_vk(message, tags, access_token, owner_id):
    full_message = f"{message}\n\n{tags}"
    params = {
        'access_token': access_token,
        'v': '5.131',
        'message': full_message,
        'owner_id': owner_id,
        'from_group': 1
    }
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=10)
        data = r.json()
        return 'response' in data
    except Exception as e:
        print(f"VK ошибка: {e}")
        return False
