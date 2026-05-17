# Словарь для отслеживания неудачных попыток
failed_attempts = {}
BLOCK_TIME = 3600  # 1 час блокировки
MAX_ATTEMPTS = 3

def send_email_alert(user_id, ip=None):
    """Отправляет уведомление на почту (через простой SMTP или через бота)"""
    # Вариант 1: через бота в личку
    # bot.send_message(ADMIN_USER_ID, f"⚠️ Попытка взлома админки! user_id={user_id}, ip={ip}")
    
    # Вариант 2: через почту (нужен SMTP)
    import smtplib
    from email.message import EmailMessage
    msg = EmailMessage()
    msg.set_content(f"Неудачная попытка входа в админку бота.\nUser ID: {user_id}\nIP: {ip}\nВремя: {datetime.now()}")
    msg['Subject'] = '[Бот] Попытка взлома админки'
    msg['From'] = os.environ.get("ALERT_EMAIL_FROM")
    msg['To'] = os.environ.get("ALERT_EMAIL_TO")
    # ... отправка через SMTP

def is_blocked(user_id):
    """Проверяет, заблокирован ли пользователь"""
    if user_id in failed_attempts:
        attempts, block_until = failed_attempts[user_id]
        if time.time() < block_until:
            return True
        else:
            del failed_attempts[user_id]
    return False

def register_failed_attempt(user_id, ip=None):
    """Регистрирует неудачную попытку и при необходимости блокирует"""
    if user_id in failed_attempts:
        attempts, block_until = failed_attempts[user_id]
        attempts += 1
        if attempts >= MAX_ATTEMPTS:
            block_until = time.time() + BLOCK_TIME
            send_email_alert(user_id, ip)
        failed_attempts[user_id] = (attempts, block_until)
    else:
        failed_attempts[user_id] = (1, 0)

# В handle_admin_command добавить:
def handle_admin_command(message, bot):
    user_id = message.from_user.id
    
    # Проверка на блокировку
    if is_blocked(user_id):
        bot.reply_to(message, "❌ Доступ заблокирован на 1 час из-за слишком частых неудачных попыток.")
        return
    
    if user_id != ADMIN_USER_ID:
        register_failed_attempt(user_id)  # фиксируем попытку
        bot.reply_to(message, "❌ Доступ запрещён.")
        return

    parts = message.text.split()
    if len(parts) == 2 and parts[1] == ADMIN_PASSWORD:
        authorize_admin(user_id, parts[1])
        log_admin_action(user_id, "login", "success")
        # Очищаем историю неудачных попыток при успешном входе
        failed_attempts.pop(user_id, None)
        bot.reply_to(message, "✅ Авторизован. Ваше меню:", reply_markup=get_admin_menu())
    else:
        register_failed_attempt(user_id)  # фиксируем неудачную попытку
        bot.reply_to(message, "❌ Неверный пароль. Попробуйте: #админ <пароль>")
