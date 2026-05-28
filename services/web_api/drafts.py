# ==========================================
# Файл: services/web_api/drafts.py
# Справка: README.md → Веб-морда / API / Черновики
# Задача: эндпоинты для работы с черновиками
# Комментарий: вызовы из веб-морды
# Зависит от: flask, services.draft_builder, debug_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from services.draft_builder import list_drafts, create_draft, get_draft, update_draft, delete_draft
from debug_utils import debug_log

drafts_bp = Blueprint('drafts', __name__)

def log_d(level, message):
    debug_log("WEB_API_DRAFTS", message, level)

@drafts_bp.route('/list', methods=['GET'])
def list_drafts_api():
    return jsonify(list_drafts())

@drafts_bp.route('/create', methods=['POST'])
def create_draft_api():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        return jsonify({"error": "Title and content required"}), 400
    draft = create_draft(title, content, data.get('media'), data.get('tags'))
    return jsonify(draft)

@drafts_bp.route('/get/<int:draft_id>', methods=['GET'])
def get_draft_api(draft_id):
    draft = get_draft(draft_id)
    if not draft:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify(draft)

@drafts_bp.route('/update/<int:draft_id>', methods=['POST'])
def update_draft_api(draft_id):
    data = request.json
    success = update_draft(draft_id, **data)
    if not success:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify({"status": "ok"})

@drafts_bp.route('/delete/<int:draft_id>', methods=['POST'])
def delete_draft_api(draft_id):
    success = delete_draft(draft_id)
    if not success:
        return jsonify({"error": "Draft not found"}), 404
    return jsonify({"status": "ok"})
