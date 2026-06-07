# ==========================================
# Файл: dialogue/admin/__init__.py
# Задача: импорт всех публичных функций из подмодулей админки
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
    show_quotes_panel,
    handle_quotes_list,
    handle_quotes_add_start,
    handle_quotes_interval,
    handle_quotes_set_interval
)
from .posts import (
    show_add_post_ui,
    handle_vk_post,
    set_publish_interval_ui
)
