import requests
import os

def post_to_telegram(bot, chat_id, message, file_path=None, tags=None):
    # Добавляем теги к сообщению, если они есть
    full_message = message
    if tags and message:
        full_message = f"{message}\n\n{tags}"
    elif tags and not message:
        full_message = tags
    
    try:
        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                with open(file_path, 'rb') as f:
                    if full_message:
                        bot.send_photo(chat_id, f, caption=full_message, parse_mode='Markdown')
                    else:
                        bot.send_photo(chat_id, f)
            elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                with open(file_path, 'rb') as f:
                    if full_message:
                        bot.send_video(chat_id, f, caption=full_message, parse_mode='Markdown')
                    else:
                        bot.send_video(chat_id, f)
            else:
                with open(file_path, 'rb') as f:
                    if full_message:
                        bot.send_document(chat_id, f, caption=full_message, parse_mode='Markdown')
                    else:
                        bot.send_document(chat_id, f)
        else:
            if full_message:
                bot.send_message(chat_id, full_message, parse_mode='Markdown')
            else:
                print(f"[PUBLISHER] Нет текста и файла для публикации в {chat_id}")
                return False
        return True
    except Exception as e:
        print(f"[PUBLISHER] Ошибка Telegram: {e}")
        return False

def post_to_vk(message, tags, access_token, owner_id, file_path=None):
    full_message = f"{message}\n\n{tags}" if message else tags
    params = {
        'access_token': access_token,
        'v': '5.131',
        'message': full_message,
        'owner_id': owner_id,
        'from_group': 1
    }
    
    if file_path and os.path.exists(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            upload_url = get_upload_url(access_token, owner_id)
            if upload_url:
                photo_attachment = upload_photo_to_vk(upload_url, file_path, access_token)
                if photo_attachment:
                    params['attachments'] = photo_attachment
        else:
            print(f"[PUBLISHER] VK: неподдерживаемый тип файла {ext}")
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=10)
        data = r.json()
        if 'response' in data:
            print(f"[PUBLISHER] VK: опубликовано")
            return True
        else:
            print(f"[PUBLISHER] VK ошибка: {data}")
            return False
    except Exception as e:
        print(f"[PUBLISHER] VK исключение: {e}")
        return False

def get_upload_url(access_token, owner_id):
    params = {
        'access_token': access_token,
        'v': '5.131',
        'owner_id': owner_id
    }
    try:
        r = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params, timeout=10)
        data = r.json()
        return data.get('response', {}).get('upload_url')
    except Exception as e:
        print(f"[PUBLISHER] VK upload URL ошибка: {e}")
        return None

def upload_photo_to_vk(upload_url, file_path, access_token):
    try:
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            r = requests.post(upload_url, files=files)
            data = r.json()
        
        save_params = {
            'access_token': access_token,
            'v': '5.131',
            'photo': data['photo'],
            'server': data['server'],
            'hash': data['hash']
        }
        r = requests.get('https://api.vk.com/method/photos.saveWallPhoto', params=save_params)
        photo_data = r.json()
        
        if 'response' in photo_data and photo_data['response']:
            photo = photo_data['response'][0]
            return f"photo{photo['owner_id']}_{photo['id']}"
        else:
            print(f"[PUBLISHER] VK save photo ошибка: {photo_data}")
            return None
    except Exception as e:
        print(f"[PUBLISHER] VK upload photo ошибка: {e}")
        return None
