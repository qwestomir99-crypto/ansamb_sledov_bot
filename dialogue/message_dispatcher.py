# ==========================================
# Файл: dialogue/message_dispatcher.py
# Справка: README.md → Диспетчер сообщений
# Задача: обработка всех сообщений без register_next_step_handler
# Комментарий: поддерживает диалог, цитаты, посты (с медиа)
# ==========================================

import os
import time
from datetime import datetime
from debug_utils import debug_log
from dialogue.agent import ask_agent
from dialogue.quotes import add_quote, set_quotes_interval
from dialogue.post_manager import add_post_to_pool
from dialogue.admin_commands import is_admin_authorized
from dialogue.button_map import get_admin_menu_keyboard
from dialogue.state_manager import user_states, post_drafts, clear_state

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
                clear_state(user_id)
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
            
            clear_state(user_id)
            return
        
        # === ДОБАВЛЕНИЕ ЦИТАТЫ ===
        if state == "waiting_quote_text":
            quote = message.text.strip()
            if quote:
                success = add_quote(quote)
                if success:
                    bot.reply_to(message, "✅ *Цитата добавлена в базу!*", parse_mode='Markdown')
                else:
                    bot.reply_to(message, "❌ *Ошибка при сохранении цитаты.*", parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ *Текст цитаты не может быть пустым.*", parse_mode='Markdown')
            
            clear_state(user_id)
            return
        
        # === УСТАНОВКА ИНТЕРВАЛА ЦИТАТ ===
        if state == "waiting_quote_interval":
            try:
                interval = int(message.text.strip())
                if 5 <= interval <= 720:
                    set_quotes_interval(interval)
                    bot.reply_to(message, f"✅ *Интервал цитат установлен на {interval} минут.*", parse_mode='Markdown')
                else:
                    bot.reply_to(message, "❌ *Ошибка: введите число от 5 до 720.*", parse_mode='Markdown')
            except ValueError:
                bot.reply_to(message, "❌ *Ошибка: введите целое число.*", parse_mode='Markdown')
            
            clear_state(user_id)
            return
        
        # === ДОБАВЛЕНИЕ ПОСТА ===
        if state == "waiting_simple_post":
            if message.text == "/cancel":
                bot.reply_to(message, "❌ Добавление поста отменено.")
                clear_state(user_id)
                # Возвращаем админ-меню
                if is_admin_authorized(user_id):
                    bot.send_message(
                        message.chat.id,
                        "🛡️ *Админ-меню*",
                        reply_markup=get_admin_menu_keyboard(),
                        parse_mode='Markdown'
                    )
                return
            
            # Определяем текст (caption для медиа, иначе обычный текст)
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
            
            # Сохраняем пост
            success = add_post_to_pool(text, tags, author=str(user_id), source="tg", media_url=media_file_id)
            
            if success:
                bot.reply_to(message, "✅ *Пост добавлен в пул публикаций!*", parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ *Ошибка при сохранении поста.*", parse_mode='Markdown')
            
            # Возвращаем админ-меню
            if is_admin_authorized(user_id):
                bot.send_message(
                    message.chat.id,
                    "🛡️ *Админ-меню*",
                    reply_markup=get_admin_menu_keyboard(),
                    parse_mode='Markdown'
                )
            
            clear_state(user_id)
            return
        
        # === ЕСЛИ НЕТ СОСТОЯНИЯ — ИГНОРИРУЕМ ===
        return
