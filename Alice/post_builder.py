# ==========================================
# Файл: Alice/post_builder.py
# Справка: README.md → Алиса / Сборщик постов
# Задача: логика Алисы для предложения контента и сборки постов
# Комментарий: использует draft_builder.py для создания черновиков
# Зависит от: services.draft_builder, services.tracking, debug_utils
# Вызывается из: Alice/core.py
# ==========================================

from services.draft_builder import create_draft
from services.tracking import track_track, track_picture
from debug_utils import debug_log

def log_pb(level, message):
    debug_log("ALICE_POST_BUILDER", message, level)

def suggest_post(topic, mood="neutral"):
    """
    Алиса предлагает структуру поста на основе темы.
    """
    log_pb("INFO", f"Предложение поста на тему: {topic}")
    
    # 1. Генерация текста
    text_prompt = f"Напиши короткий пост на тему '{topic}'. Стиль: аутентичный, ритм 0,8 Гц."
    from Alice.core import generate_alice_response
    text = generate_alice_response(text_prompt)
    
    # 2. Поиск подходящего трека
    track_result = track_track(topic)
    track_url = track_result["url"] if track_result else None
    
    # 3. Поиск подходящей картины
    picture_result = track_picture(topic)
    picture_url = picture_result["url"] if picture_result else None
    
    # 4. Сборка черновика
    draft = create_draft(
        title=topic,
        content=text,
        media=[track_url, picture_url] if track_url or picture_url else None,
        tags=[mood, "Ансамбль", "0,8 Гц"]
    )
    
    return draft
