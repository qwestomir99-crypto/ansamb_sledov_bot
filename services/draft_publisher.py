# ==========================================
# Файл: services/draft_publisher.py
# Справка: README.md → Публикация черновиков
# Задача: публикация черновиков в VK и Telegram
# Комментарий: использует tg_api и vk_api для отправки
# Зависит от: services.tg_api, services.vk_api, debug_utils
# Вызывается из: services.web_api.drafts
# ==========================================

from services.tg_api import send_telegram_message
from services.vk_api import send_vk_post
from debug_utils import debug_log
from services.draft_builder import get_draft

def log_dp(level, message):
    debug_log("DRAFT_PUBLISHER", message, level)

def publish_draft(draft_id, platform):
    """
    Публикует черновик в указанной платформе.
    """
    draft = get_draft(draft_id)
    if not draft:
        log_dp("ERROR", f"Черновик {draft_id} не найден")
        return False
    
    content = draft.get("content", "")
    tags = " ".join(draft.get("tags", []))
    full_text = f"{content}\n\n{tags}"
    
    if platform == "telegram":
        success = send_telegram_message(full_text)
        if success:
            log_dp("INFO", f"Черновик {draft_id} опубликован в Telegram")
        else:
            log_dp("ERROR", f"Ошибка публикации в Telegram")
        return success
    elif platform == "vk":
        success = send_vk_post(full_text)
        if success:
            log_dp("INFO", f"Черновик {draft_id} опубликован в VK")
        else:
            log_dp("ERROR", f"Ошибка публикации в VK")
        return success
    else:
        log_dp("ERROR", f"Неизвестная платформа: {platform}")
        return False
