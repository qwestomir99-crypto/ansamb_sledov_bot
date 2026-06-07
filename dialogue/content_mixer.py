# ==========================================
# Файл: dialogue/content_mixer.py
# Справка: README.md → Content Mixer
# Задача: сборка постов из VK-фото + цитат + YouTube-видео по тегам
# Комментарий: без YandexGPT, на шаблонах и пересечении тегов
# ==========================================

import random
from debug_utils import debug_log

def get_mixed_post():
    """Собирает пост из фото VK + цитаты + видео YouTube"""
    
    photo_post = None
    try:
        from services.photo_reader import get_random_post
        photo_post = get_random_post()
    except: pass
    
    if not photo_post:
        return None
    
    photo_url = photo_post.get('photo_url')
    photo_text = photo_post.get('text', '')
    photo_tags = photo_post.get('tags', [])
    
    debug_log("MIXER", f"Фото: {photo_text[:50]}...")
    
    quote = None
    try:
        from services.sqlite_client import get_quotes_list
        quotes = get_quotes_list()
        if quotes:
            matching = [q for q in quotes if any(tag.lower() in q.lower() for tag in photo_tags)]
            quote = random.choice(matching) if matching else random.choice(quotes)
    except:
        quote = "Ритм 0,8 Гц стабилен. Сеть тлеет."
    
    debug_log("MIXER", f"Цитата: {quote[:50] if quote else 'нет'}...")
    
    video = None
    try:
        from dialogue.youtube_auto import get_random_video
        video = get_random_video()
    except: pass
    
    post_text = photo_text if photo_text else ""
    if quote: post_text += f"\n\n📜 {quote}"
    if video and video.get('url'): post_text += f"\n\n🎬 {video['title']}\n{video['url']}"
    
    all_tags = set(photo_tags)
    if video: all_tags.add("#YouTube")
    all_tags.add("#СапёрыАутентичности")
    post_text += f"\n\n{' '.join(all_tags)}"
    
    if len(post_text) > 1024: post_text = post_text[:1020] + "..."
    
    return {"text": post_text, "photo_url": photo_url, "tags": list(all_tags)}

def publish_mixed_post(bot, chat_id):
    post = get_mixed_post()
    if not post:
        debug_log("MIXER", "Не удалось собрать пост")
        return False
    try:
        if post.get('photo_url'):
            bot.send_photo(chat_id, post['photo_url'], caption=post['text'][:1024])
        else:
            bot.send_message(chat_id, post['text'])
        debug_log("MIXER", "Микс-пост опубликован")
        return True
    except Exception as e:
        debug_log("MIXER", f"Ошибка публикации: {e}", "ERROR")
        return False
