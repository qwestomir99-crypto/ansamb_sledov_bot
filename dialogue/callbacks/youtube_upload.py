# ==========================================
# Файл: dialogue/callbacks/youtube_upload.py
# Справка: README.md → Обработчики кнопок / YouTube Upload
# Задача: обработка кнопки "Загрузить на YouTube"
# Комментарий: открывает веб-морду на вкладке YouTube
# Зависит от: telebot, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from debug_utils import debug_log

def register_youtube_upload_callbacks(bot: telebot.TeleBot, config: dict):
    @bot.callback_query_handler(func=lambda call: call.data == "youtube_upload")
    def callback_youtube_upload(call):
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🎬 Для загрузки видео на YouTube перейдите в веб-морду.\n\n"
            "Нажмите кнопку «Загрузить видео» в блоке YouTube Upload."
        )
