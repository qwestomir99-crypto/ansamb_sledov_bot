# ==========================================
# Файл: services/error_handlers.py
# Справка: README.md → Веб-морда / Обработка ошибок
# Задача: красивые страницы ошибок (400, 401, 403, 404, 405, 500, 502, 503)
# Комментарий: все ошибки логируются и показывают единую страницу error.html
# Зависит от: flask, debug_utils
# Вызывается из: services/app.py
# ==========================================

from flask import render_template, redirect, url_for
from debug_utils import debug_log

def register_error_handlers(app):
    """Регистрирует обработчики ошибок в приложении Flask"""
    
    @app.errorhandler(400)
    def bad_request(e):
        debug_log("ERROR_HANDLER", f"400 Bad Request: {str(e)}", "ERROR")
        return render_template('error.html', 
                             error_code='400', 
                             error_message='Неверный запрос. Проверь параметры или вернись на главную.'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        debug_log("ERROR_HANDLER", f"401 Unauthorized: {str(e)}", "WARNING")
        return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        debug_log("ERROR_HANDLER", f"403 Forbidden: {str(e)}", "WARNING")
        return render_template('error.html', 
                             error_code='403', 
                             error_message='Доступ запрещён. У тебя нет прав для просмотра этой страницы.'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        debug_log("ERROR_HANDLER", f"404 Not Found: {e}", "WARNING")
        return render_template('error.html', 
                             error_code='404', 
                             error_message='Страница не найдена. Проверь URL или вернись на главную.'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        debug_log("ERROR_HANDLER", f"405 Method Not Allowed: {str(e)}", "WARNING")
        return render_template('error.html', 
                             error_code='405', 
                             error_message='Метод запроса не поддерживается для этой страницы.'), 405

    @app.errorhandler(500)
    def internal_error(e):
        debug_log("ERROR_HANDLER", f"500 Internal Server Error: {str(e)}", "ERROR")
        return render_template('error.html', 
                             error_code='500', 
                             error_message='Внутренняя ошибка сервера. Сапёры уже работают над восстановлением.'), 500

    @app.errorhandler(502)
    def bad_gateway(e):
        debug_log("ERROR_HANDLER", f"502 Bad Gateway: {str(e)}", "ERROR")
        return render_template('error.html', 
                             error_code='502', 
                             error_message='Ошибка шлюза. Возможно, сервер перегружен. Попробуй позже.'), 502

    @app.errorhandler(503)
    def service_unavailable(e):
        debug_log("ERROR_HANDLER", "503 Service Unavailable", "ERROR")
        return render_template('error.html', 
                             error_code='503', 
                             error_message='Сервис временно недоступен. Сапёры уже чинят.'), 503
