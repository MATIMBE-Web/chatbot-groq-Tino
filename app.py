from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
import re
from urllib.parse import quote_plus

app = Flask(__name__)
CORS(app)

# ============================================================
# CHAVES API
# ============================================================
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')
API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ============================================================
# PERSONALIDADES
# ============================================================
PERSONALITIES = {
    "default": "Você é um assistente útil. Responda em português.",
    "professor": "Você é um professor. Ensine de forma didática. Responda em português.",
    "programador": "Você é um programador. Escreva código explicado. Responda em português.",
    "chef": "Você é um chef. Dê receitas e dicas. Responda em português.",
    "financeiro": "Você é um consultor financeiro. Responda em português.",
    "fitness": "Você é um personal trainer. Responda em português.",
    "coach": "Você é um coach. Responda em português."
}

# Modelos disponíveis na Groq (atualizados 2026)
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",      # Melhor qualidade
    "llama-3.1-70b-versatile",      # Alta qualidade
    "llama-3.1-8b-instant",         # Rápido e bom
    "gemma2-9b-it",                 # Google Gemma 2
    "deepseek-r1-distill-llama-70b" # DeepSeek
]

# ============================================================
# FUNÇÃO DE PESQUISA NA WEB
# ============================================================

def search_web(query):
    """Pesquisa na web usando a API do DuckDuckGo (gratuita)"""
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
        else:
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

        # Detectar se deve pesquisar
        search_keywords = ['pesquisar', 'buscar', 'procurar', 'google', 'internet', 'atual', 'agora', 'notícia', 'evento']
        should_search = search_enabled or any(kw in user_message.lower() for kw in search_keywords)
        
        search_results_text = ""
        results = []
        if should_search:
            print(f"🔍 Pesquisando: {user_message}")
            results = search_web(user_message)
            if results:
                search_results_text = format_search_results(results)
                print(f"✅ Encontrados {len(results)} resultados")
            else:
                search_results_text = "Não foi possível obter resultados da pesquisa."

        # Construir prompt
        if search_results_text:
            prompt = f"""{system_prompt}

Informações atualizadas da internet sobre a pergunta do usuário:
{search_results_text}

Com base nas informações acima, responda à pergunta do usuário de forma completa e útil, citando as fontes quando possível.

Pergunta do usuário: {user_message}

Resposta:"""
        else:
            prompt = f"""{system_prompt}

Pergunta do usuário: {user_message}

Resposta:"""

        # Chamar a API
        for model in MODELS:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
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
                        'search_used': should_search,
                        'search_results': results if should_search else []
                    }), 200
            except Exception as e:
                print(f"Erro com {model}: {str(e)}")
                continue

        return jsonify({'error': 'Nenhum modelo disponível'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# ROTAS ADICIONAIS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor Groq - Português',
        'models': MODELS,
        'search_available': True
    }), 200

@app.route('/api/search', methods=['POST'])
def search_only():
    try:
        data = request.json
        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Consulta vazia'}), 400
        
        results = search_web(query)
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# ============================================================
# INICIALIZAÇÃO
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🔍 CHATBOT COM PESQUISA NA WEB")
    print("🚀 Rodando em http://localhost:5000")
    print("📋 Modelos disponíveis:", MODELS)
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=10000)