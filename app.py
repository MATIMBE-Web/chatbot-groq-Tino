from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app)

# ============================================================
# CHAVE API
# ============================================================
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')
GROQ_API_KEY = GROQ_API_KEY.strip()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ============================================================
# PERSONALIDADES
# ============================================================
PERSONALITIES = {
    "default": "Voce e um assistente util. Responda em portugues.",
    "professor": "Voce e um professor. Ensine de forma didatica. Responda em portugues.",
    "programador": "Voce e um programador. Escreva codigo explicado. Responda em portugues.",
    "chef": "Voce e um chef. De receitas e dicas. Responda em portugues.",
    "financeiro": "Voce e um consultor financeiro. Responda em portugues.",
    "fitness": "Voce e um personal trainer. Responda em portugues.",
    "coach": "Voce e um coach. Responda em portugues."
}

# ============================================================
# MODELOS
# ============================================================
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "deepseek-r1-distill-llama-70b"
]

# ============================================================
# PESQUISA NA WEB
# ============================================================
def search_web(query):
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&pretty=1"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Resultado'),
                    'snippet': data.get('Abstract', ''),
                    'link': data.get('AbstractURL', '#')
                })
            for item in data.get('RelatedTopics', [])[:5]:
                if 'Text' in item:
                    text = item['Text']
                    link = item.get('FirstURL', '#')
                    parts = text.split(' - ', 1)
                    title = parts[0] if len(parts) > 0 else text[:50]
                    snippet = parts[1] if len(parts) > 1 else text
                    results.append({
                        'title': title[:100],
                        'snippet': snippet[:300],
                        'link': link
                    })
            return results[:5]
        return []
    except Exception as e:
        print(f"Erro na pesquisa: {str(e)}")
        return []

def format_search_results(results):
    if not results:
        return "Nenhum resultado encontrado."
    formatted = "Resultados da pesquisa:\n\n"
    for i, r in enumerate(results, 1):
        formatted += f"{i}. {r['title']}\n"
        formatted += f"   {r['snippet']}\n"
        if r['link'] and r['link'] != '#':
            formatted += f"   Link: {r['link']}\n"
        formatted += "\n"
    return formatted

# ============================================================
# ROTA PRINCIPAL
# ============================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        personality_key = data.get('personality', 'default')
        search_enabled = data.get('search', False)

        if not messages:
            return jsonify({'error': 'Nenhuma mensagem'}), 400

        user_message = messages[-1]['content'] if messages else ""
        system_prompt = PERSONALITIES.get(personality_key, PERSONALITIES["default"])

        search_results_text = ""
        results = []

        if search_enabled:
            results = search_web(user_message)
            if results:
                search_results_text = format_search_results(results)

        if search_results_text:
            prompt = system_prompt + "\n\nInformacoes da pesquisa:\n" + search_results_text + "\nPergunta: " + user_message + "\nResposta:"
        else:
            prompt = system_prompt + "\n\nPergunta: " + user_message + "\nResposta:"

        for model in AVAILABLE_MODELS:
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 800
                }
                response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    return jsonify({
                        'content': result['choices'][0]['message']['content'],
                        'model': f'groq/{model}',
                        'personality': personality_key,
                        'search_used': search_enabled,
                        'search_results': results if search_enabled else []
                    }), 200
            except Exception as e:
                print(f"Erro com {model}: {str(e)}")
                continue

        return jsonify({'error': 'Nenhum modelo disponivel'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# ROTAS ADICIONAIS
# ============================================================
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor Groq - Portugues',
        'models': AVAILABLE_MODELS,
        'search_available': True
    }), 200

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# ============================================================
# INICIALIZACAO
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("CHATBOT COM PESQUISA NA WEB")
    print("Rodando em http://localhost:5000")
    print("Modelos:", AVAILABLE_MODELS)
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=10000)