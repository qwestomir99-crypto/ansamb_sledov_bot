# ==========================================
# Файл: services/web_api/drafts.py
# Справка: README.md → Веб-морда / API / Черновики
# Задача: эндпоинты для работы с черновиками
# Комментарий: добавлена защита @login_required
# Зависит от: flask, services.draft_builder, services.draft_publisher, debug_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from services.draft_builder import list_drafts, create_draft, get_draft, update_draft, delete_draft
from services.draft_publisher import publish_draft
from debug_utils import debug_log
from services.auth_decorator import login_required

drafts_bp = Blueprint('drafts', __name__)

def log_d(level, message):
    debug_log("WEB_API_DRAFTS", message, level)

@drafts_bp.route('/list', methods=['GET'])
@login_required
def list_drafts_api():
    return jsonify(list_drafts())

@drafts_bp.route('/create', methods=['POST'])
@login_required
def create_draft_api():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        return jsonify({"error": "Title and content required"}), 400
    draft = create_draft(title, content, data.get('media'), data.get('tags'))
    return jsonify(draft)

@drafts_bp.route('/get/<int:draft_id>', methods=['GET'])
@login_required
def get_draft_api(draft_id):
    draft = get_draft(draft_id)
    if not draft:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify(draft)

@drafts_bp.route('/update/<int:draft_id>', methods=['POST'])
@login_required
def update_draft_api(draft_id):
    data = request.json
    success = update_draft(draft_id, **data)
    if not success:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify({"status": "ok"})

@drafts_bp.route('/delete/<int:draft_id>', methods=['POST'])
@login_required
def delete_draft_api(draft_id):
    success = delete_draft(draft_id)
    if not success:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify({"status": "ok"})

@drafts_bp.route('/publish/<int:draft_id>', methods=['POST'])
@login_required
def publish_draft_api(draft_id):
    data = request.json
    platform = data.get('platform')
    if not platform:
        return jsonify({"error": "Platform required"}), 400
    success = publish_draft(draft_id, platform)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"error": "Publish failed"}), 500
