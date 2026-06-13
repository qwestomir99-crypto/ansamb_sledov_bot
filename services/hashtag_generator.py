# ==========================================
# Файл: services/hashtag_generator.py
# Задача: генерация хэштегов по тексту поста
# ==========================================

import sqlite3
import re
from datetime import datetime

DB_PATH = 'data/ansambl.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_all_hashtags():
    """Возвращает все хэштеги из базы"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT tag, category, weight FROM hashtags ORDER BY weight DESC")
    rows = c.fetchall()
    conn.close()
    return [{"tag": r[0], "category": r[1], "weight": r[2]} for r in rows]

def extract_keywords(text):
    """Извлекает ключевые слова из текста (простейший вариант)"""
    words = re.findall(r'[а-яА-Яa-zA-Z]{4,}', text.lower())
    return set(words)

def suggest_hashtags(text, limit=5):
    """Предлагает хэштеги на основе текста"""
    keywords = extract_keywords(text)
    all_tags = get_all_hashtags()
    
    scored = []
    for tag_info in all_tags:
        tag_clean = tag_info['tag'].lower().replace('#', '')
        score = 0
        for kw in keywords:
            if kw in tag_clean or tag_clean in kw:
                score += tag_info['weight']
        if score > 0:
            scored.append((tag_info['tag'], score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored[:limit]]

def add_hashtag(tag, category='user', weight=1):
    """Добавляет новый хэштег в базу"""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO hashtags (tag, category, weight) VALUES (?, ?, ?)", (tag, category, weight))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка добавления хэштега: {e}")
        return False
    finally:
        conn.close()

def get_popular_hashtags(limit=10):
    """Возвращает самые популярные хэштеги"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT tag, weight FROM hashtags ORDER BY weight DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]
