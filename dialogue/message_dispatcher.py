# ==========================================
# Файл: dialogue/message_dispatcher.py
# Справка: README.md → Диспетчер сообщений
# Задача: обработка всех сообщений без register_next_step_handler
# Комментарий: управление состояниями пользователей
# ==========================================

from debug_utils import debug_log
from dialogue.agent import ask_agent

# Глобальные словари
user_states = {}      # {user_id: "waiting_post_text" / "waiting_post_tags" / "waiting_dialog"}
post_drafts = {}      # {user_id: {"text": "...", "tags": [...]}}

def register_dispatcher(bot):
    """Регистрирует универсальный обработчик сообщений"""
    
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        user_id = message.from_user.id
        state = user_states.get(user_id)
        
        # === ДИАЛОГ С АГЕНТОМ ===
        if state == "waiting_dialog":
            if message.text == "/cancel":
                bot.reply_to(message, "❌ Диалог отменён.")
                user_states.pop(user_id, None)
                return
            
            status_msg = bot.reply_to(message, "⏳ Старший брат думает...")
            answer = ask_agent(message.text, user_id=user_id)
            
            try:
                bot.delete_message(status_msg.chat.id, status_msg.message_id)
            except:
                pass
            
            if answer:
                bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
            else:
                bot.reply_to(message, "🌙 Старший брат отдыхает. Попробуй позже.")
            return
        
        # === ДОБАВЛЕНИЕ ПОСТА: ШАГ 1 — ТЕКСТ ===
        if state == "waiting_post_text":
            post_drafts[user_id] = {"text": message.text}
            user_states[user_id] = "waiting_post_tags"
            bot.reply_to(message, "📝 *Текст сохранён!* Теперь введите теги (через пробел) или /skip", parse_mode='Markdown')
            return
        
        # === ДОБАВЛЕНИЕ ПОСТА: ШАГ 2 — ТЕГИ ===
        if state == "waiting_post_tags":
            tags = [] if message.text == "/skip" else message.text.split()
            text = post_drafts.get(user_id, {}).get("text")
            
            if text:
                from dialogue.post_manager import add_post_to_pool
                success = add_post_to_pool(text, tags, author_id=user_id)
                if success:
                    bot.reply_to(message, "✅ *Пост добавлен в пул публикаций!*", parse_mode='Markdown')
                else:
                    bot.reply_to(message, "❌ *Ошибка при сохранении поста.*", parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ *Ошибка: текст не найден. Начните заново.*", parse_mode='Markdown')
            
            user_states.pop(user_id, None)
            post_drafts.pop(user_id, None)
            return
        
        # === ЕСЛИ НЕТ СОСТОЯНИЯ — ИГНОРИРУЕМ ===
        # (не мешаем другим обработчикам)
