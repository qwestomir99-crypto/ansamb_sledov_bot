# ==========================================
# Файл: dialogue/message_dispatcher.py
# Справка: README.md → Диспетчер сообщений
# Задача: обработка сообщений в группах (замена register_next_step_handler)
# Комментарий: поддерживает добавление постов с фото/видео
# ==========================================

from debug_utils import debug_log
from dialogue.post_manager import add_post_to_pool
from dialogue.admin_commands import is_admin_authorized
from dialogue.button_map import get_admin_menu_keyboard

# Словарь состояний пользователей
user_states = {}

def register_dispatcher(bot):
    """Регистрирует универсальный обработчик сообщений"""
    
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        user_id = message.from_user.id
        state = user_states.get(user_id)
        
        # === ОЖИДАНИЕ ПОСТА ===
        if state == "waiting_for_post":
            debug_log("DISPATCHER", f"Получен пост от {user_id}", "INFO")
            
            if message.text == "/cancel":
                bot.reply_to(message, "❌ Добавление поста отменено.")
                user_states.pop(user_id, None)
                
                # Возвращаем админ-меню
                if is_admin_authorized(user_id):
                    bot.send_message(
                        message.chat.id,
                        "🛡️ *Админ-меню*",
                        reply_markup=get_admin_menu_keyboard(),
                        parse_mode='Markdown'
                    )
                return
            
            # Определяем текст (caption для фото/видео, иначе обычный текст)
            text = message.caption if message.photo or message.video else message.text
            if not text:
                bot.reply_to(message, "❌ Добавьте текст к посту (описание картинки или видео).")
                return
            
            # Извлекаем теги из текста
            tags = [word for word in text.split() if word.startswith('#')]
            
            # Получаем file_id (если есть фото или видео)
            media_file_id = None
            if message.photo:
                media_file_id = message.photo[-1].file_id
            elif message.video:
                media_file_id = message.video.file_id
            
            # Сохраняем пост в пул
            success = add_post_to_pool(text, tags, author=str(user_id), source="tg", media_url=media_file_id)
            
            if success:
                bot.reply_to(message, "✅ *Пост добавлен в пул публикаций!*", parse_mode='Markdown')
                debug_log("DISPATCHER", f"Пост сохранён: {text[:50]}...", "INFO")
            else:
                bot.reply_to(message, "❌ *Ошибка при сохранении поста.*", parse_mode='Markdown')
                debug_log("DISPATCHER", "Ошибка сохранения поста", "ERROR")
            
            # Возвращаем админ-меню
            if is_admin_authorized(user_id):
                bot.send_message(
                    message.chat.id,
                    "🛡️ *Админ-меню*",
                    reply_markup=get_admin_menu_keyboard(),
                    parse_mode='Markdown'
                )
            
            user_states.pop(user_id, None)
            return
        
        # === ЕСЛИ НЕТ СОСТОЯНИЯ — ИГНОРИРУЕМ ===
        return
