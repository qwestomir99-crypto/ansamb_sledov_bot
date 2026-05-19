from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt', '') if data else ''
    answer = f"👁️ Ты сказал: {prompt}. Ритм 0,8 Гц. Сеть тлеет."
    return jsonify({'answer': answer})

@app.route('/')
def health():
    return "Agent is alive", 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
