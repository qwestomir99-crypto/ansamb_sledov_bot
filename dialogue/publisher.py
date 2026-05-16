import requests
import os

def post_to_telegram(bot, chat_id, message):
    try:
        bot.send_message(chat_id, message, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"Ошибка публикации в Telegram: {e}")
        return False

def post_to_vk(message, tags, access_token, owner_id, group_id=None):
    """
    Публикует на стену VK (группы или пользователя)
    """
    full_message = f"{message}\n\n{tags}"
    params = {
        'access_token': access_token,
        'v': '5.131',
        'message': full_message,
        'owner_id': owner_id,
        'from_group': 1 if group_id else 0
    }
    try:
        response = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=10)
        data = response.json()
        if 'response' in data:
            return True
        else:
            print(f"VK ошибка: {data}")
            return False
    except Exception as e:
        print(f"VK публикация ошибка: {e}")
        return False
