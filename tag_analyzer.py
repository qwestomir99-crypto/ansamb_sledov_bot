# ==========================================
# Файл: tag_analyzer.py
# Задача: анализ тегов в постах (post_pool.json и VK)
# Комментарий: запускается вручную или через GitHub Actions.
#              Экспорт в CSV, отчёты в JSON, поиск по тегам.
# ==========================================
#!/usr/bin/env python3
# tag_analyzer.py — запускается вручную или через GitHub Actions

import json
import csv
import os
import argparse
import logging
import sys
from datetime import datetime
from collections import Counter

# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
POST_POOL_FILE = "dialogue/data/post_pool.json"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"
LOG_FILE = "analytics/tag_analyzer.log"
OUTPUT_DIR = "analytics"

def setup_logging():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def log_error(e, context=""):
    logging.error(f"{context}: {type(e).__name__} - {e}")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ===== БЕЗОПАСНАЯ РАБОТА С ФАЙЛАМИ =====
def safe_load_json(filepath, default=None):
    if default is None:
        default = []
    try:
        if not os.path.exists(filepath):
            logging.warning(f"Файл не найден: {filepath}")
            return default
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log_error(e, f"Ошибка парсинга {filepath}")
        return default
    except Exception as e:
        log_error(e, f"Ошибка чтения {filepath}")
        return default

def safe_save_json(filepath, data):
    try:
        ensure_dir(os.path.dirname(filepath))
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Сохранён: {filepath}")
        return True
    except Exception as e:
        log_error(e, f"Ошибка сохранения {filepath}")
        return False

# ===== ЗАГРУЗКА ДАННЫХ =====
def load_posts():
    return safe_load_json(POST_POOL_FILE, [])

def load_vk_posts():
    return safe_load_json(VK_POSTS_FILE, [])

# ===== АНАЛИЗ ТЕГОВ =====
def extract_tags_from_post(post):
    return post.get("tags", [])

def extract_tags_from_text(text):
    words = text.split()
    return [w for w in words if w.startswith('#')]

def tag_statistics(posts, source="pool"):
    all_tags = []
    for post in posts:
        if source == "pool":
            tags = extract_tags_from_post(post)
        else:
            tags = extract_tags_from_text(post.get("text", ""))
        all_tags.extend(tags)
    return Counter(all_tags)

def search_by_tag(tag, posts):
    tag = tag.lower().strip('#')
    result = []
    for post in posts:
        post_tags = [t.lower().strip('#') for t in post.get("tags", [])]
        if tag in post_tags:
            result.append(post)
    return result

# ===== ЭКСПОРТ =====
def export_to_csv(posts, filename, output_dir=OUTPUT_DIR):
    try:
        ensure_dir(output_dir)
        output_path = f"{output_dir}/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "tags", "author", "weight", "added", "last_posted", "source"])
            for p in posts:
                writer.writerow([
                    p.get("text", ""),
                    ",".join(p.get("tags", [])),
                    p.get("author", ""),
                    p.get("weight", 50),
                    p.get("added", ""),
                    p.get("last_posted", ""),
                    p.get("source", "")
                ])
        logging.info(f"Экспорт CSV: {output_path}")
        print(f"✅ Экспорт: {output_path}")
    except Exception as e:
        log_error(e, "Экспорт CSV")

# ===== ГЕНЕРАЦИЯ ОТЧЁТОВ =====
def generate_report(posts, source="pool", output_dir=OUTPUT_DIR):
    try:
        ensure_dir(output_dir)
        tag_counter = tag_statistics(posts, source)
        
        report = {
            "generated": datetime.now().isoformat(),
            "source": source,
            "total_posts": len(posts),
            "unique_tags": len(tag_counter),
            "top_tags": tag_counter.most_common(20),
            "avg_weight": sum(p.get("weight", 50) for p in posts) / len(posts) if posts else 0
        }
        
        report_path = f"{output_dir}/report_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        safe_save_json(report_path, report)
        
        print(f"✅ Отчёт: {report_path}")
        print(f"\n📊 Сводка ({source}):")
        print(f"   - Всего постов: {report['total_posts']}")
        print(f"   - Уникальных тегов: {report['unique_tags']}")
        print(f"   - Средний вес: {report['avg_weight']:.1f}")
        print(f"\n🔥 Топ-10 тегов:")
        for tag, count in report['top_tags'][:10]:
            print(f"   #{tag}: {count}")
        
        return report
    except Exception as e:
        log_error(e, "Генерация отчёта")
        return None

def generate_combined_report():
    try:
        ensure_dir(OUTPUT_DIR)
        
        pool_posts = load_posts()
        vk_posts = load_vk_posts()
        
        pool_tags = tag_statistics(pool_posts, "pool")
        vk_tags = tag_statistics(vk_posts, "vk")
        
        common_tags = set(pool_tags.keys()) & set(vk_tags.keys())
        
        report = {
            "generated": datetime.now().isoformat(),
            "pool": {
                "total_posts": len(pool_posts),
                "top_tags": pool_tags.most_common(20)
            },
            "vk": {
                "total_posts": len(vk_posts),
                "top_tags": vk_tags.most_common(20)
            },
            "common_tags": list(common_tags),
            "recommendations": []
        }
        
        for tag, vk_count in vk_tags.most_common(10):
            if tag not in pool_tags or pool_tags[tag] < vk_count / 2:
                report["recommendations"].append(f"Добавь контент с тегом {tag} (популярен в VK)")
        
        report_path = f"{OUTPUT_DIR}/combined_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        safe_save_json(report_path, report)
        
        print(f"✅ Общий отчёт: {report_path}")
        print(f"\n📊 Сводка VK: {len(vk_posts)} постов")
        print(f"🔥 Топ-5 тегов VK:")
        for tag, count in vk_tags.most_common(5):
            print(f"   #{tag}: {count}")
        
        return report
    except Exception as e:
        log_error(e, "Генерация общего отчёта")
        return None

# ===== ОСНОВНАЯ ФУНКЦИЯ =====
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Экспорт постов в CSV")
    parser.add_argument("--report", action="store_true", help="Генерация отчётов")
    parser.add_argument("--combined", action="store_true", help="Генерация общего отчёта (пул + VK)")
    parser.add_argument("--tag", type=str, help="Поиск по тегу в пуле постов")
    args = parser.parse_args()
    
    setup_logging()
    logging.info("=== tag_analyzer.py запущен ===")
    
    if args.tag:
        posts = load_posts()
        found = search_by_tag(args.tag, posts)
        print(f"🔍 Найдено {len(found)} постов с тегом #{args.tag}:")
        for p in found[:10]:
            print(f"   - {p.get('text', '')[:60]}...")
        logging.info(f"Поиск по тегу #{args.tag}: найдено {len(found)} постов")
    else:
        if args.export:
            posts = load_posts()
            export_to_csv(posts, "post_pool")
            vk_posts = load_vk_posts()
            if vk_posts:
                export_to_csv(vk_posts, "vk_posts")
            logging.info("Экспорт CSV выполнен")
        if args.report:
            posts = load_posts()
            generate_report(posts, "pool")
            vk_posts = load_vk_posts()
            if vk_posts:
                generate_report(vk_posts, "vk")
            logging.info("Генерация отчётов выполнена")
        if args.combined:
            generate_combined_report()
            logging.info("Генерация общего отчёта выполнена")
        if not any([args.export, args.report, args.combined, args.tag]):
            generate_combined_report()
            logging.info("Запуск по умолчанию: общий отчёт")
    
    logging.info("=== tag_analyzer.py завершён ===")

if __name__ == "__main__":
    main()
