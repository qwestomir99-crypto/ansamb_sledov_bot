# ==========================================
# Файл: dialogue/message_dispatcher.py
# Справка: README.md → Диспетчер сообщений
# Задача: обработка сообщений в группах (замена register_next_step_handler)
# ==========================================

from debug_utils import debug_log
from dialogue.post_manager import add_post_to_pool
from dialogue.admin_commands import is_admin_authorized
from dialogue.button_map import get_admin_menu_keyboard

user_states = {}

def register_dispatcher(bot):
    
    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        user_id = message.from_user.id
        state = user_states.get(user_id)
        
        if state == "waiting_for_post":
            if message.text == "/cancel":
                bot.reply_to(message, "❌ Отменено")
                user_states.pop(user_id, None)
                return
            
            text = message.caption if message.photo else message.text
            if not text:
                bot.reply_to(message, "❌ Нет текста")
                return
            
            tags = [word for word in text.split() if word.startswith('#')]
            file_id = message.photo[-1].file_id if message.photo else None
            
            success = add_post_to_pool(text, tags, author=str(user_id), source="tg", media_url=file_id)
            
            if success:
                bot.reply_to(message, "✅ Пост добавлен!")
            else:
                bot.reply_to(message, "❌ Ошибка")
            
            if is_admin_authorized(user_id):
                bot.send_message(message.chat.id, "🛡️ Админ-меню", reply_markup=get_admin_menu_keyboard())
            
            user_states.pop(user_id, None)
