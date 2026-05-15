import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Конфигурация Yandex GPT (берётся из переменных окружения)
API_KEY = os.environ.get("YC_API_KEY")
FOLDER_ID = os.environ.get("YC_FOLDER_ID")
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "no prompt"}), 400

    if not API_KEY or not FOLDER_ID:
        return jsonify({"error": "Yandex GPT not configured"}), 500

    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {"stream": False, "temperature": 0.7, "maxTokens": 2000},
        "messages": [{"role": "user", "text": prompt}]
    }
    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("AGENT_PORT", 5001))
    app.run(host='0.0.0.0', port=port)
