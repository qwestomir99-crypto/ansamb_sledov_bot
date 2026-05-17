#!/usr/bin/env python3
# tag_analyzer.py — запускается из GitHub Actions или вручную

import json
import csv
import os
from datetime import datetime
from collections import Counter
from pathlib import Path

def load_posts(pool_path="dialogue/data/post_pool.json"):
    if not os.path.exists(pool_path):
        return []
    with open(pool_path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_by_tag(tag, pool_path="dialogue/data/post_pool.json"):
    posts = load_posts(pool_path)
    tag = tag.lower().strip('#')
    result = []
    for p in posts:
        post_tags = [t.lower().strip('#') for t in p.get("tags", [])]
        if tag in post_tags:
            result.append(p)
    return result

def tag_statistics(pool_path="dialogue/data/post_pool.json"):
    posts = load_posts(pool_path)
    all_tags = []
    for p in posts:
        all_tags.extend([t.lower().strip('#') for t in p.get("tags", [])])
    return Counter(all_tags)

def export_to_csv(pool_path="dialogue/data/post_pool.json", output_dir="analytics"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    posts = load_posts(pool_path)
    output_path = f"{output_dir}/posts_export_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "tags", "author", "weight", "added", "last_posted", "source"])
        for p in posts:
            writer.writerow([
                p["text"],
                ",".join(p.get("tags", [])),
                p.get("author", ""),
                p.get("weight", 50),
                p.get("added", ""),
                p.get("last_posted", ""),
                p.get("source", "")
            ])
    print(f"✅ Экспорт: {output_path}")

def generate_report(pool_path="dialogue/data/post_pool.json", output_dir="analytics"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    posts = load_posts(pool_path)
    tag_counter = tag_statistics(pool_path)
    
    report = {
        "generated": datetime.now().isoformat(),
        "total_posts": len(posts),
        "unique_tags": len(tag_counter),
        "top_tags": tag_counter.most_common(20),
        "posts_by_source": Counter(p.get("source", "unknown") for p in posts),
        "avg_weight": sum(p.get("weight", 50) for p in posts) / len(posts) if posts else 0
    }
    
    report_path = f"{output_dir}/report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Отчёт: {report_path}")
    print(f"\n📊 Сводка:")
    print(f"   - Всего постов: {report['total_posts']}")
    print(f"   - Уникальных тегов: {report['unique_tags']}")
    print(f"   - Средний вес: {report['avg_weight']:.1f}")
    print(f"\n🔥 Топ-10 тегов:")
    for tag, count in report['top_tags'][:10]:
        print(f"   #{tag}: {count}")
    
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Экспорт в CSV")
    parser.add_argument("--report", action="store_true", help="Сгенерировать отчёт")
    parser.add_argument("--tag", type=str, help="Поиск по тегу")
    args = parser.parse_args()
    
    if args.tag:
        posts = search_by_tag(args.tag)
        print(f"🔍 Найдено {len(posts)} постов с тегом #{args.tag}:")
        for p in posts[:10]:
            print(f"   - {p['text'][:60]}...")
    else:
        if args.export:
            export_to_csv()
        if args.report:
            generate_report()
