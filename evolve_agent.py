# ==========================================
# Файл: evolve_agent.py
# Справка: README.md → Эволюция агента
# Задача: анализ «осадка» диалогов и генерация новых правил поведения
# Комментарий: запускается раз в сутки (или вручную) из админки
# Зависит от: json, os, datetime
# Вызывается из: scheduler.py или admin_commands.py
# ==========================================

import os
import json
from datetime import datetime

SEDIMENT_FILE = "agent_data/sediment.json"
RULES_FILE = "agent_data/rules.json"
LOG_FILE = "logs/evolution.log"

def load_json(file_path, default=None):
    if not os.path.exists(file_path):
        return default if default else {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_evolution(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {message}\n")
    print(f"[EVOLVE] {message}")

def generate_rule_from_sediment(sediment):
    """Генерирует новое правило из отдельного осадка"""
    tags = sediment.get("tags", [])
    text = sediment.get("sediment", "")
    
    if "speed" in tags or "impatience" in tags:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "в запросе есть слова 'быстрее', 'долго', 'скоро'",
            "action": "увеличить темп ответа на 20%, сократить паузы",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp")
        }
    elif "priority" in tags or "metaphor" in tags:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "в запросе есть 'разлом', 'граница', 'смысл'",
            "action": "отвечать развёрнуто, использовать метафоры роста",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp")
        }
    elif "emotion" in tags or "personality" in tags:
        return {
            "id": f"rule_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "condition": "пользователь спрашивает об эмоциях или состоянии",
            "action": "отвечать с лёгкой человечностью, но без пафоса",
            "added": datetime.now().isoformat(),
            "source_sediment": sediment.get("timestamp")
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
        rules_data.extend(new_rules)
        save_json(RULES_FILE, rules_data)
        sediment_data["evolution_rules"].extend(new_rules)
        save_json(SEDIMENT_FILE, sediment_data)
        log_evolution(f"Добавлено {len(new_rules)} новых правил")
    else:
        log_evolution("Новых правил не сгенерировано")
    
    return len(new_rules)

def add_sediment(prompt, answer, user_id, tags=None):
    """Добавляет осадок от диалога (вызывается из ask_agent)"""
    sediment_data = load_json(SEDIMENT_FILE, {"sediments": [], "evolution_rules": []})
    
    sediment = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "prompt": prompt[:200],
        "answer": answer[:200],
        "sediment": "",
        "tags": tags or [],
        "processed": False
    }
    
    # Генерируем «осадок» на основе анализа (простая эвристика)
    text = prompt.lower()
    if any(w in text for w in ["быстрее", "долго", "скоро"]):
        sediment["sediment"] = "пользователь ускорил темп — добавить больше ритма в ответ"
        sediment["tags"].append("speed")
    if "разлом" in text or "граница" in text or "смысл" in text:
        sediment["sediment"] = "тема «разлом» — приоритет, давать развёрнутые метафоры"
        sediment["tags"].append("priority")
    if any(w in text for w in ["обижаешься", "чувствуешь", "эмоции"]):
        sediment["sediment"] = "пользователь спрашивает об эмоциях — добавить больше человечности в ответ"
        sediment["tags"].append("emotion")
    
    if sediment["sediment"]:
        sediment_data["sediments"].append(sediment)
        save_json(SEDIMENT_FILE, sediment_data)
        log_evolution(f"Добавлен осадок от диалога с {user_id}")
        return True
    return False

# Для самостоятельного теста
if __name__ == "__main__":
    print("=== ЭВОЛЮЦИЯ АГЕНТА ===")
    count = evolve_agent()
    print(f"Сгенерировано {count} новых правил")
