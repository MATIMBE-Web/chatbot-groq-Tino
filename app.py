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
# FUNÇÃO DE PESQUISA - GOOGLE
# ============================================================

# Coloque aqui suas chaves
GOOGLE_API_KEY = os.environ.get('AQ.Ab8RN6I-GgYuh9kQ1Fj-ORob_rpBksMagRIwJ4VN9IdZ6rN8Rg')
GOOGLE_CSE_ID = os.environ.get('AQ.Ab8RN6I-GgYuh9kQ1Fj-ORob_rpBksMagRIwJ4VN9IdZ6rN8Rg')

def search_web(query):
    """Pesquisa na web usando Google Custom Search API (gratuita)"""
    try:
        print(f"🔍 A pesquisar: {query}")
        
        # Usar a API do Google
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={quote_plus(query)}&num=5"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', 'Sem título'),
                    'snippet': item.get('snippet', 'Sem descrição'),
                    'link': item.get('link', '#')
                })
            
            print(f"✅ Encontrados {len(results)} resultados")
            return results
        else:
            print(f"❌ Erro na pesquisa: {response.status_code} - {response.text[:100]}")
            return []
            
    except Exception as e:
        print(f"❌ Erro na pesquisa: {str(e)}")
        return []
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