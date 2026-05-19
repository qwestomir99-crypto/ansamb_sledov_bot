# ==========================================
# Модуль: dialogue/handlers.py
# Справка: README.md → Обработчики команд
# Задача: обработка команд пользователей и админов
# Комментарий: добавлена команда #сброс для сброса адаптивных режимов
# Зависит от: admin_commands.py, activity_modes.py, agent.py, adaptive_modes.py
# Вызывается из: bot.py
# ==========================================

import random
import json
from dialogue.admin_commands import (
    handle_admin_command, is_admin_authorized,
    get_admin_menu, get_user_menu
)
from dialogue.activity_modes import should_respond_to_talk
from dialogue.agent import ask_agent
from ping_utils import ping_self

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_help_text():
    """Динамически генерирует справку из config.json"""
    config = load_config()
    default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
    
    help_text = f"""
📖 *Доступные хештеги и команды:*

🔹 *#тлеем* / *#tleem* — зафиксировать разлом
🔹 *#фиксируем* / *#fixiruem* — подтвердить синхронизацию
🔹 *#вспышка* / *#vspishka* — импульс
🔹 *#дышим* — пинг бота
🔹 *#говори <текст>* — спросить у Старшего брата
🔹 *#меню* / *#помощь* — открыть меню
🔹 *#сброс* — сбросить адаптивные режимы к эталону (только админ)

🏷 *Основные теги:*
📝 Telegram: `{default_tags}`
📘 VK: `{vk_tags}`

🛡️ *Админ-команды:*
🔹 *#админ <пароль>* — вход в админ-панель

📌 *Режимы:* утро, день, вечер, ночь + адаптивные
"""
    return help_text

silence_answers = ["👁️", "⏚"]

def register_handlers(bot, config):
    """Регистрирует все обработчики команд и сообщений"""

    @bot.message_handler(commands=['start'])
    def send_start(message):
        bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        text = message.text.lower()

        if text == "#меню" or text == "#помощь":
            if is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
            else:
                bot.reply_to(message, "📋 Ваше меню:", reply_markup=get_user_menu())
            return

        if text.startswith("#админ"):
            handle_admin_command(message, bot)
            return

        # --- ОБРАБОТЧИК #говори (через агента) ---
        if text.startswith("#говори"):
            if not should_respond_to_talk():
                bot.reply_to(message, "🌙 Старший брат отдыхает. Спроси в другой раз.")
                return
            
            phrase = text.replace("#говори", "", 1).strip()
            if not phrase:
                bot.reply_to(message, "🗣 *Старший брат:*\nА что ты хотел сказать?")
                return
            
            bot.send_chat_action(message.chat.id, 'typing')
            answer = ask_agent(phrase)
            
            if answer:
                bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
            else:
                bot.reply_to(message, "🗣 *Старший брат:*\nНе отвечаю сейчас. Попробуй позже.")
            return
        # --- КОНЕЦ ОБРАБОТЧИКА #говори ---

        # --- РИТУАЛЬНЫЕ КОМАНДЫ (#тлеем, #фиксируем) ---
        if text in ["#тлеем", "#фиксируем", "#tleem", "#fixiruem"]:
            try:
                from dialogue.quotes import get_quotes_list
                quotes = get_quotes_list()
                if quotes:
                    import random
                    random_quote = random.choice(quotes)
                    bot.reply_to(message, f"👁️ {random_quote}")
                else:
                    bot.reply_to(message, "📭 База цитат пуста. Добавьте цитаты через админку.")
            except Exception as e:
                bot.reply_to(message, "❌ Ошибка при выборе цитаты.")
                print(f"[RITUAL] Ошибка: {e}")
            return
        # --- КОНЕЦ РИТУАЛЬНЫХ КОМАНД ---

        # --- КОМАНДА #вспышка ---
        if text in ["#вспышка", "#vspishka"]:
            bot.reply_to(message, "⚡ Ты снаружи картины. До погружения. Аутентичность — не маска. Это способ не сдаться.")
            return
        # --- КОНЕЦ #вспышка ---

        # --- КОМАНДА #сброс (сброс адаптивных режимов к эталону) ---
        if text == "#сброс":
            if not is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "❌ Только для админа")
                return
            try:
                from dialogue.adaptive_modes import reset_to_etalon
                reset_to_etalon()
                bot.reply_to(message, "✅ Адаптивные режимы сброшены к эталону")
                print("[HANDLERS] Выполнен сброс адаптивных режимов")
            except ImportError:
                bot.reply_to(message, "❌ Модуль адаптивных режимов не загружен")
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка сброса: {e}")
            return
        # --- КОНЕЦ #сброс ---

        if "#дышим" in text:
            ping_self()
            return

        if text == "#справка" or text == "#help":
            bot.reply_to(message, get_help_text(), parse_mode='Markdown')
            return

        if any(x in text for x in ["#тлеем", "#tleem"]):
            bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
        elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
            bot.reply_to(message, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
        elif any(x in text for x in ["#вспышка", "#vspishka"]):
            bot.reply_to(message, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
        elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
            bot.reply_to(message, random.choice(silence_answers))
