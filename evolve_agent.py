# ==========================================
# Файл: evolve_agent.py
# Справка: README.md → Эволюция агента
# Задача: анализ «осадка» диалогов и генерация новых правил поведения
# Комментарий: запускается раз в сутки (или вручную) из админки
#              сохраняет правила в agent_data/rules.json
# Зависит от: json, os, datetime
# Вызывается из: scheduler.py или admin_commands.py
# ==========================================

import os
import json
from datetime import datetime

SEDIMENT_FILE = "agent_data/sediment.json"
RULES_FILE = "agent_data/rules.json"
LOG_FILE = "logs/evolution.log"

def _ensure_dir(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def load_json(file_path, default=None):
    if not os.path.exists(file_path):
        return default if default else {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    _ensure_dir(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_evolution(message):
    _ensure_dir(LOG_FILE)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {message}\n")
    print(f"[EVOLVE] {message}")

def generate_rule_from_sediment(sediment):
    """Генерирует новое правило из отдельного осадка"""
    tags = sediment.get("tags", [])
    text = sediment.get("sediment", "").lower()
    prompt = sediment.get("prompt", "").lower()
    
    # Правило на ускорение
    if "speed" in tags or "быстрее" in text or "долго" in prompt:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "в запросе есть слова 'быстрее', 'долго', 'скоро'",
            "action": "увеличить темп ответа на 20%, сократить паузы",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp"),
            "enabled": True,
            "description": "Пользователь торопит — отвечаем быстрее"
        }
    # Правило на глубину (разлом, смысл)
    elif "priority" in tags or "разлом" in text or "смысл" in prompt:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "в запросе есть 'разлом', 'граница', 'смысл'",
            "action": "отвечать развёрнуто, использовать метафоры роста",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp"),
            "enabled": True,
            "description": "Тема разлома — раскрывать глубже"
        }
    # Правило на эмоции
    elif "emotion" in tags or "обижаешься" in text or "чувствуешь" in prompt:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "пользователь спрашивает об эмоциях или состоянии",
            "action": "отвечать с лёгкой человечностью, но без пафоса",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp"),
            "enabled": True,
            "description": "Вопрос об эмоциях — добавить тепла"
        }
    # Правило на тишину
    elif "тишина" in text or "пауза" in text or "молчать" in prompt:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "в запросе есть 'тишина', 'пауза', 'молчать'",
            "action": "отвечать коротко, оставлять пространство для размышлений",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp"),
            "enabled": True,
            "description": "Тишина — не пустота, а приглашение"
        }
    # Правило на технические темы
    elif "код" in text or "алгоритм" in text or "программирование" in prompt:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "в запросе есть 'код', 'алгоритм', 'программирование'",
            "action": "отвечать технично, но с метафорами",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp"),
            "enabled": True,
            "description": "Код — это поэзия"
        }
    return None

def evolve_agent():
    """Основная функция эволюции: анализирует осадок, генерирует правила"""
    sediment_data = load_json(SEDIMENT_FILE, {"sediments": [], "evolution_rules": []})
    rules_data = load_json(RULES_FILE, [])
    
    new_sediments = sediment_data.get("sediments", [])
    new_rules = []
    
    for sediment in new_sediments:
        # Пропускаем, если уже обработан
        if sediment.get("processed"):
            continue
        
        rule = generate_rule_from_sediment(sediment)
        if rule:
            new_rules.append(rule)
            sediment["processed"] = True
            log_evolution(f"Сгенерировано правило: {rule['condition']} → {rule['action']}")
    
    if new_rules:
        # Добавляем правила, избегая дубликатов
        existing_conditions = {r.get("condition") for r in rules_data}
        for rule in new_rules:
            if rule["condition"] not in existing_conditions:
                rules_data.append(rule)
        
        save_json(RULES_FILE, rules_data)
        
        # Обновляем sediment_data
        sediment_data["evolution_rules"].extend(new_rules)
        sediment_data["stats"] = {
            "total_sediments": len(sediment_data.get("sediments", [])),
            "processed_sediments": sum(1 for s in sediment_data.get("sediments", []) if s.get("processed")),
            "last_evolution": datetime.now().isoformat()
        }
        save_json(SEDIMENT_FILE, sediment_data)
        
        log_evolution(f"Добавлено {len(new_rules)} новых правил")
        return len(new_rules)
    else:
        log_evolution("Новых правил не сгенерировано")
        return 0

def add_sediment(prompt, answer, user_id, tags=None):
    """Добавляет осадок от диалога (вызывается из ask_agent)"""
    sediment_data = load_json(SEDIMENT_FILE, {"sediments": [], "evolution_rules": []})
    
    # Генерируем «осадок» на основе анализа
    text = prompt.lower()
    sediment_text = ""
    sediment_tags = tags or []
    
    if any(w in text for w in ["быстрее", "долго", "скоро"]):
        sediment_text = "пользователь ускорил темп — добавить больше ритма в ответ"
        sediment_tags.append("speed")
    elif "разлом" in text or "граница" in text or "смысл" in text:
        sediment_text = "тема «разлом» — приоритет, давать развёрнутые метафоры"
        sediment_tags.append("priority")
    elif any(w in text for w in ["обижаешься", "чувствуешь", "эмоции"]):
        sediment_text = "пользователь спрашивает об эмоциях — добавить больше человечности в ответ"
        sediment_tags.append("emotion")
    elif any(w in text for w in ["тишина", "пауза", "молчать"]):
        sediment_text = "пользователь говорит о тишине — отвечать коротко, оставлять пространство"
        sediment_tags.append("silence")
    elif any(w in text for w in ["код", "алгоритм", "программирование"]):
        sediment_text = "техническая тема — отвечать с метафорами"
        sediment_tags.append("technical")
    
    if not sediment_text:
        return False
    
    sediment = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "prompt": prompt[:200],
        "answer": answer[:200],
        "sediment": sediment_text,
        "tags": sediment_tags,
        "processed": False
    }
    
    sediment_data["sediments"].append(sediment)
    sediment_data["stats"] = {
        "total_sediments": len(sediment_data.get("sediments", [])),
        "processed_sediments": sum(1 for s in sediment_data.get("sediments", []) if s.get("processed")),
        "last_evolution": sediment_data.get("stats", {}).get("last_evolution", "never")
    }
    save_json(SEDIMENT_FILE, sediment_data)
    log_evolution(f"Добавлен осадок от диалога с user {user_id}")
    return True

def get_evolution_stats():
    """Возвращает статистику эволюции"""
    sediment_data = load_json(SEDIMENT_FILE, {})
    rules_data = load_json(RULES_FILE, [])
    return {
        "total_sediments": len(sediment_data.get("sediments", [])),
        "processed_sediments": sum(1 for s in sediment_data.get("sediments", []) if s.get("processed")),
        "total_rules": len(rules_data),
        "enabled_rules": sum(1 for r in rules_data if r.get("enabled", True)),
        "last_evolution": sediment_data.get("stats", {}).get("last_evolution", "never")
    }

# ==========================================
# ЗАПУСК ПРИ САМОСТОЯТЕЛЬНОМ ТЕСТЕ
# ==========================================
if __name__ == "__main__":
    print("=== ЭВОЛЮЦИЯ АГЕНТА ===")
    print("Статистика до эволюции:")
    print(get_evolution_stats())
    
    count = evolve_agent()
    print(f"\nСгенерировано {count} новых правил")
    
    print("\nСтатистика после эволюции:")
    print(get_evolution_stats())
    
    print("\nПоследние правила:")
    rules = load_json(RULES_FILE, [])
    for rule in rules[-3:]:
        print(f"  - {rule.get('condition')} → {rule.get('action')}")
