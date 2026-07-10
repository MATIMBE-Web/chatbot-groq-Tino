from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'SUA_CHAVE_GROQ_AQUI')
API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

PERSONALITIES = {
    "default": "Você é um assistente útil. Responda em português.",
    "professor": "Você é um professor. Ensine de forma didática. Responda em português.",
    "programador": "Você é um programador. Escreva código explicado. Responda em português.",
    "chef": "Você é um chef. Dê receitas e dicas. Responda em português.",
    "financeiro": "Você é um consultor financeiro. Responda em português.",
    "fitness": "Você é um personal trainer. Responda em português.",
    "coach": "Você é um coach. Responda em português."
}

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it"
]

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        personality_key = data.get('personality', 'default')
        
        if not messages:
            return jsonify({'error': 'Nenhuma mensagem'}), 400

        user_message = messages[-1]['content'] if messages else ""
        system_prompt = PERSONALITIES.get(personality_key, PERSONALITIES["default"])

        for model in MODELS:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
                
                response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    return jsonify({
                        'content': result['choices'][0]['message']['content'],
                        'model': f'groq/{model}',
                        'personality': personality_key
                    }), 200
            except Exception as e:
                continue

        return jsonify({'error': 'Nenhum modelo disponível'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor Groq - Português',
        'models': MODELS
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)