from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# SUA CHAVE OPENROUTER (crie em https://openrouter.ai/keys)
OPENROUTER_API_KEY = "SUA_CHAVE_OPENROUTER"

# Modelos com bom custo-benefício
MODELS = [
    "google/gemini-2.0-flash-001",  # Muito barato
    "meta-llama/llama-3.2-3b-instruct",
    "mistralai/mistral-7b-instruct",
    "qwen/qwen-2.5-7b-instruct",
]

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        user_message = messages[-1]['content'] if messages else ""
        
        for model in MODELS:
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                    },
                    data=json.dumps({
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "Réponds toujours en français."},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }),
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return jsonify({
                        'content': result['choices'][0]['message']['content'],
                        'model': model
                    }), 200
                else:
                    print(f"❌ {model} falhou: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Erro com {model}: {str(e)[:50]}")
                continue
        
        return jsonify({'error': 'Nenhum modelo disponível'}), 503
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Servidor rodando em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
