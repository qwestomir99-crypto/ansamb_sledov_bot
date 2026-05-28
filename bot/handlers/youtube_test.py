# ==========================================
# Файл: bot/handlers/youtube_test.py
# Справка: README.md → Обработчики команд / YouTube тест
# Задача: команда #ютуб_тест
# ==========================================

def register_youtube_test_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() == "#ютуб_тест")
    def handle_youtube_test(message):
        try:
            from services.youtube_reader import test_youtube
            bot.send_chat_action(message.chat.id, 'typing')
            success = test_youtube()
            if success:
                bot.reply_to(message, "✅ YouTube API работает! Последнее видео получено.")
            else:
                bot.reply_to(message, "❌ YouTube API не отвечает. Проверь ключи и ID канала.")
        except ImportError:
            bot.reply_to(message, "❌ Модуль youtube_reader не загружен")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка: {e}")
