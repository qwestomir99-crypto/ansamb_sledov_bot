# ==========================================
# Файл: dialogue/journalist.py
# Справка: README.md → Журналист / Аналитика
# Задача: анализ тегов и слов из VK и пула постов, генерация рекомендаций
# Комментарий: сохраняет сводку в journalist_feed.json для последующего использования
# Зависит от: json, time, collections, datetime
# Вызывается из: bot.py (отдельный поток, если ENABLE_JOURNALIST = True)
# ==========================================

import time
import json
import os
from datetime import datetime
from collections import Counter

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')
VK_POSTS_FILE = "dialogue/data/vk_posts.json"
POST_POOL_FILE = "dialogue/data/post_pool.json"
JOURNALIST_FEED = "dialogue/data/journalist_feed.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_vk_posts():
    if not os.path.exists(VK_POSTS_FILE):
        return []
    with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_post_pool():
    if not os.path.exists(POST_POOL_FILE):
        return []
    with open(POST_POOL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_journalist_feed(feed):
    os.makedirs(os.path.dirname(JOURNALIST_FEED), exist_ok=True)
    with open(JOURNALIST_FEED, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

def extract_tags_from_text(text):
    """Извлекает хештеги из текста"""
    words = text.split()
    tags = [w for w in words if w.startswith('#')]
    return tags

def analyze_vk_posts(posts, limit=10):
    """Анализирует посты VK: топ тегов, популярные фразы"""
    all_tags = []
    all_texts = []
    
    for post in posts:
        text = post.get("text", "")
        if text:
            all_texts.append(text)
            tags = extract_tags_from_text(text)
            all_tags.extend(tags)
    
    tag_counter = Counter(all_tags)
    top_tags = tag_counter.most_common(limit)
    
    # Простой анализ частоты слов (без стоп-слов)
    words = []
    stop_words = ['это', 'все', 'как', 'и', 'в', 'на', 'с', 'по', 'к', 'у', 'не', 'да', 'нет', 'или', 'но', 'за', 'под', 'над', 'для', 'без', 'через', 'между']
    for text in all_texts:
        for word in text.lower().split():
            word_clean = word.strip('.,!?;:()[]{}"\'')
            if len(word_clean) > 3 and word_clean not in stop_words and not word_clean.startswith('#'):
                words.append(word_clean)
    
    word_counter = Counter(words)
    top_words = word_counter.most_common(limit)
    
    return {
        "total_posts": len(posts),
        "top_tags": top_tags,
        "top_words": top_words,
        "last_updated": datetime.now().isoformat()
    }

def analyze_post_pool(posts, limit=10):
    """Анализирует пул постов"""
    all_tags = []
    for post in posts:
        tags = post.get("tags", [])
        all_tags.extend(tags)
    
    tag_counter = Counter(all_tags)
    top_tags = tag_counter.most_common(limit)
    
    return {
        "total_posts": len(posts),
        "top_tags": top_tags,
        "last_updated": datetime.now().isoformat()
    }

def generate_recommendations(vk_analytics, pool_analytics):
    """Генерирует рекомендации для писателя"""
    recommendations = []
    
    # Что крутить: теги, популярные в VK, но ещё не в пуле
    vk_top_tags = set([tag for tag, count in vk_analytics.get("top_tags", [])])
    pool_top_tags = set([tag for tag, count in pool_analytics.get("top_tags", [])])
    
    new_tags = vk_top_tags - pool_top_tags
    if new_tags:
        recommendations.append(f"Попробуй добавить посты с тегами: {', '.join(list(new_tags)[:3])}")
    
    # Популярные слова из VK
    top_words = vk_analytics.get("top_words", [])
    if top_words:
        recommendations.append(f"В тренде слова: {', '.join([w for w, c in top_words[:5]])}")
    
    if not recommendations:
        recommendations.append("Пока нет явных трендов. Публикуй лучшее из пула.")
    
    return recommendations

def journalist_loop(bot, TG_CHAT_ID):
    """Журналист: анализирует данные и сохраняет сводку для писателя"""
    config = load_config()
    if not config.get("journalist", {}).get("enabled", True):
        print("[JOURNALIST] Отключён в конфиге")
        return
    
    interval_hours = config.get("journalist", {}).get("interval_hours", 24)
    interval_seconds = interval_hours * 3600
    
    print(f"[JOURNALIST] Запущен, интервал {interval_hours} часов")
    
    while True:
        try:
            # Загружаем данные
            vk_posts = load_vk_posts()
            post_pool = load_post_pool()
            
            # Анализируем
            vk_analytics = analyze_vk_posts(vk_posts)
            pool_analytics = analyze_post_pool(post_pool)
            recommendations = generate_recommendations(vk_analytics, pool_analytics)
            
            # Формируем сводку для писателя
            feed = {
                "timestamp": datetime.now().isoformat(),
                "vk_analytics": vk_analytics,
                "pool_analytics": pool_analytics,
                "recommendations": recommendations
            }
            save_journalist_feed(feed)
            
            print(f"[JOURNALIST] Сводка сохранена. VK постов: {len(vk_posts)}, в пуле: {len(post_pool)}")
            
        except Exception as e:
            print(f"[JOURNALIST] Ошибка: {e}")
        
        time.sleep(interval_seconds)
