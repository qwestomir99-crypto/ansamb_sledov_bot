# ==========================================
# Блок: мгновенный пост в VK (с фото и видео) — ИСПРАВЛЕННЫЙ
# ==========================================

def handle_callback_vk_post(bot, chat_id, message_id, user_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст поста для VK (можно с хештегами):")
    bot.register_next_step_handler(msg, process_vk_post_text, bot, chat_id, user_id)

def process_vk_post_text(message, bot, chat_id, user_id):
    text = message.text.strip()
    if not text:
        bot.send_message(chat_id, "❌ Текст не может быть пустым")
        return_to_admin_menu(bot, chat_id, user_id=user_id)
        return
    msg = bot.send_message(chat_id, "📎 Пришлите фото, видео или нажмите /skip")
    bot.register_next_step_handler(msg, process_vk_post_file, bot, chat_id, text, user_id)

def process_vk_post_file(message, bot, chat_id, text, user_id):
    # Определяем тип и размер файла ДО скачивания
    file_id = None
    is_video = False
    is_photo = False
    use_userbot = False
    file_size = 0
    
    # Проверяем тип сообщения
    if message.video:
        file_size = message.video.file_size
        file_id = message.video.file_id
        is_video = True
        # Видео больше 50 МБ отправляем через Userbot, НЕ вызываем bot.get_file
        if file_size > 50 * 1024 * 1024:
            use_userbot = True
            print(f"[DEBUG] Видео {file_size / 1024 / 1024:.1f} МБ -> Userbot")
    elif message.document:
        file_size = message.document.file_size
        file_id = message.document.file_id
        ext = os.path.splitext(message.document.file_name)[1].lower()
        is_video = ext in ['.mp4', '.mov', '.avi', '.mkv']
        is_photo = ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if is_video and file_size > 50 * 1024 * 1024:
            use_userbot = True
            print(f"[DEBUG] Документ-видео {file_size / 1024 / 1024:.1f} МБ -> Userbot")
    elif message.photo:
        file_size = message.photo[-1].file_size
        is_photo = True
        # Фото всегда через Bot API
    
    # Получаем токены VK
    config = load_config()
    vk_token = os.environ.get("VK_TOKEN") or config.get("vk", {}).get("token")
    vk_owner_id = os.environ.get("VK_OWNER_ID") or config.get("vk", {}).get("owner_id")
    
    if not vk_token or not vk_owner_id:
        bot.send_message(chat_id, "❌ Нет токена VK. Проверь переменные окружения.")
        return_to_admin_menu(bot, chat_id, user_id=user_id)
        return
    
    quote = get_random_quote()
    full_text = f"{text}\n\n📜 {quote}"
    auto_tags = get_auto_tags(text, "vk")
    
    # Если файл большой и это видео — используем Userbot (без скачивания через Bot API)
    if use_userbot and is_video:
        bot.send_message(chat_id, f"📹 Видео ({file_size / 1024 / 1024:.1f} МБ) отправляется через Userbot (до 2 ГБ)...")
        
        # Передаём file_id в Userbot (он скачает сам)
        from services.autoposter import upload_via_userbot
        success = upload_via_userbot(file_id, full_text, auto_tags, vk_token, vk_owner_id, message)
        
        if success:
            bot.send_message(chat_id, f"✅ Видео отправлено в VK:\n\n{full_text[:200]}")
        else:
            bot.send_message(chat_id, "❌ Ошибка при отправке видео через Userbot")
        
        return_to_admin_menu(bot, chat_id, user_id=user_id)
        return
    
    # Для маленьких файлов (до 50 МБ) используем стандартный код с Bot API
    file_path = None
    
    if message.text and message.text.lower() == "/skip":
        file_path = None
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.photo[-1].file_id}.jpg")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        print(f"[DEBUG] Фото сохранено: {file_path}")
    elif message.video:
        # Маленькое видео (до 50 МБ) — можно через Bot API
        file_info = bot.get_file(message.video.file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.video.file_id}.mp4")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        print(f"[DEBUG] Видео сохранено: {file_path}")
    elif message.document:
        ext = os.path.splitext(message.document.file_name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv']:
            file_info = bot.get_file(message.document.file_id)
            file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.document.file_id}_{message.document.file_name}")
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
            print(f"[DEBUG] Документ сохранён: {file_path}")
        else:
            bot.send_message(chat_id, "❌ Неподдерживаемый тип файла. Пост будет без вложения.")
    else:
        bot.send_message(chat_id, "❌ Неподдерживаемый тип медиа. Пост будет без вложения.")
    
    success, error_msg = post_to_vk(full_text, auto_tags, vk_token, vk_owner_id, file_path, auto_quote=False, auto_tags=False)
    
    if success:
        bot.send_message(chat_id, f"✅ Пост отправлен в VK:\n\n{full_text[:200]}")
    else:
        bot.send_message(chat_id, error_msg or "❌ Ошибка при отправке в VK")
    
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        print(f"[DEBUG] Временный файл удалён: {file_path}")
    
    return_to_admin_menu(bot, chat_id, user_id=user_id)
