# ==========================================
# Файл: dialogue/callbacks/mood.py
# Справка: README.md → Обработчики кнопок / Настроение
# Задача: обработка кнопок выбора настроения
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.button_map import get_moods_keyboard, get_callback
from dialogue.user_settings import set_user_mood, get_user_mood_name
from debug_utils import debug_log

def register_mood_callbacks(bot, config):
    
    @bot.callback_query_handler(func=lambda call: call.data == "mood_menu")
    def show_mood_menu(call):
        bot.edit_message_text(
            "🎭 *Выберите настроение*\n\n"
            "• 🎨 Художник — метафоры, образы\n"
            "• 📋 Администратор — чётко, структурированно\n"
            "• 🎭 Поэт — лирично, возвышенно\n"
            "• 🔧 Инженер — технично, по делу",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_moods_keyboard(with_back=True),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("mood_"))
    def set_mood(call):
        user_id = call.from_user.id
        mood_map = {
            "mood_artist": "artist",
            "mood_admin": "admin",
            "mood_poet": "poet",
            "mood_engineer": "engineer"
        }
        
        mood_key = call.data
        mood = mood_map.get(mood_key, "artist")
        
        set_user_mood(user_id, mood)
        mood_name = get_user_mood_name(user_id)
        
        bot.answer_callback_query(call.id, f"🎭 Настроение: {mood_name}")
        
        bot.edit_message_text(
            f"🎭 *Настроение установлено:* {mood_name}\n\n"
            "• 🎨 Художник — метафоры, образы\n"
            "• 📋 Администратор — чётко, структурированно\n"
            "• 🎭 Поэт — лирично, возвышенно\n"
            "• 🔧 Инженер — технично, по делу",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_moods_keyboard(with_back=True),
            parse_mode='Markdown'
        )
        
        debug_log("MOOD", f"Пользователь {user_id} выбрал настроение: {mood}")
    
    @bot.callback_query_handler(func=lambda call: call.data == "mood_back")
    def mood_back(call):
        from dialogue.button_map import get_admin_menu_keyboard
        bot.edit_message_text(
            "🛡️ *Админ-панель*\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_keyboard(),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
