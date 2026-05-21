# ==========================================
# Файл: new_debugger/dialogue/admin/__init__.py
# Задача: импорт всех публичных функций из подмодулей админки
# Комментарий: обновлён для поддержки дебаггера
# ==========================================

from .menu import (
    get_admin_menu,
    get_modes_submenu,
    get_content_submenu,
    get_quotes_submenu,
    get_diagnostic_submenu,
    get_user_menu,
    get_debugger_menu
)
from .auth import (
    is_admin_authorized,
    authorize_admin,
    logout_admin,
    is_blocked,
    register_failed_attempt,
    log_admin_action
)
from .quotes_admin import (
    handle_quotes_list,
    handle_quotes_add_start,
    handle_quotes_interval,
    handle_quotes_set_interval
)
from .posts import (
    handle_pub_menu,
    ask_for_post_text,
    handle_vk_post
)
from .diagnostics import (
    handle_errors,
    handle_log,
    handle_debug
)
from .callbacks import (
    handle_callback_mode,
    handle_callback_ping,
    handle_callback_toggle_alisa
)
