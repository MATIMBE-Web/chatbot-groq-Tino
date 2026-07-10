from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
import re
from urllib.parse import quote_plus
import time

app = Flask(__name__)
CORS(app)

# ============================================================
# CHAVES API
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
    "default": "Você é um assistente útil. Responda em português.",
    "professor": "Você é um professor. Ensine de forma didática. Responda em português.",
    "programador": "Você é um programador. Escreva código explicado. Responda em português.",
    "chef": "Você é um chef. Dê receitas e dicas. Responda em português.",
    "financeiro": "Você é um consultor financeiro. Responda em português.",
    "fitness": "Você é um personal trainer. Responda em português.",
    "coach": "Você é um coach. Responda em português."
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
# FUNÇÃO DE PESQUISA - CORRIGIDA
# ============================================================

def search_web(query):
    """Pesquisa na web usando a API do DuckDuckGo"""
    try:
        print(f"🔍 A pesquisar: {query}")
        
        # Usar a API do DuckDuckGo
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&pretty=1"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Resultado principal
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Resultado'),
                    'snippet': data.get('Abstract', ''),
                    'link': data.get('AbstractURL', '#')
                })
            
            # Resultados relacionados
            for item in data.get('RelatedTopics', [])[:5]:
                if 'Text' in item:
                    text = item['Text']
                    link = item.get('FirstURL', '#')
                    # Separar título do texto
                    parts = text.split(' - ', 1)
                    title = parts[0] if len(parts) > 0 else text[:50]
                    snippet = parts[1] if len(parts) > 1 else text
                    results.append({
                        'title': title[:100],
                        'snippet': snippet[:300],
                        'link': link
                    })
            
            print(f"✅ Encontrados {len(results)} resultados")
            return results
        else:
            print(f"❌ Erro na pesquisa: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro na pesquisa: {str(e)}")
        return []

def format_search_results(results):
    """Formata os resultados para o prompt"""
    if not results:
        return "Nenhum resultado encontrado."
    
    formatted = "RESULTADOS DA PESQUISA:\n\n"
    for i, r in enumerate(results, 1):
        formatted += f"{i}. {r['title']}\n"
        formatted += f"   {r['snippet']}\n"
        if r['link'] and r['link'] != '#':
            formatted += f"   Fonte: {r['link']}\n"
        formatted += "\n"
    return formatted

# ============================================================
# ROTA PRINCIPAL - CORRIGIDA
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

        print("=" * 60)
        print(f"📥 Mensagem: {user_message}")
        print(f"🔍 Pesquisa ativada: {search_enabled}")

        # ===== SEMPRE PESQUISAR SE ESTIVER ATIVADO =====
        search_results_text = ""
        results = []
        
        if search_enabled:
            print("🔍 A pesquisar na web...")
            results = search_web(user_message)
            if results:
                search_results_text = format_search_results(results)
                print(f"✅ {len(results)} resultados encontrados")
            else:
                search_results_text = "Não foi possível obter resultados da pesquisa. Responda com o seu conhecimento geral."
                print("❌ Nenhum resultado encontrado")
        else:
            print("ℹ️ Pesquisa desativada")
            search_results_text = ""

        # ===== CONSTRUIR PROMPT =====
        if search_results_text:
            prompt = f"""{system_prompt}

ATENÇÃO: O USUÁRIO ATIVOU O MODO DE PESQUISA NA WEB.
Use as informações abaixo para responder.

{search_results_text}

Com base nas informações ACIMA, responda à pergunta do usuário de forma completa, citando as fontes.
Se a informação não estiver nos resultados, diga que não encontrou e use seu conhecimento geral.

Pergunta do usuário: {user_message}

Resposta (em português, com base na pesquisa):"""
        else:
            prompt = f"""{system_prompt}

Pergunta do usuário: {user_message}

Resposta (em português):"""

        print(f"📤 Prompt enviado (primeiros 200 caracteres): {prompt[:200]}...")

        # ===== CHAMAR A API =====
        for model in AVAILABLE_MODELS:
            try:
                print(f"🔄 A tentar modelo: {model}")
                
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
                    resposta = result['choices'][0]['message']['content']
                    print(f"✅ Sucesso com {model}")
                    
                    return jsonify({
                        'content': resposta,
                        'model': f'groq/{model}',
                        'personality': personality_key,
                        'search_used': search_enabled,
                        'search_results': results if search_enabled else []
                    }), 200
                else:
                    print(f"❌ Erro no modelo {model}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exceção com {model}: {str(e)}")
                continue

        return jsonify({'error': 'Nenhum modelo disponível'}), 503
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# ROTAS ADICIONAIS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor Groq - Português',
        'models': AVAILABLE_MODELS,
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
    print("📋 Modelos disponíveis:", AVAILABLE_MODELS)
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=10000)