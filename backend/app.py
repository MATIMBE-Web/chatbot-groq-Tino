from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# ⚠️ METTEZ VOTRE CLÉ API ICI
OPENROUTER_API_KEY = "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"

# Lista de modelos gratuitos CONFIRMADOS que funcionam
FREE_MODELS = [
    # Google - Modelos gratuitos confirmados
    "google/gemini-2.0-flash-exp:free",           # Gemini 2.0 Flash Experimental
    "google/gemini-2.0-flash-001:free",            # Gemini 2.0 Flash
    
    # Meta - Modelos gratuitos confirmados
    "meta-llama/llama-3.2-3b-instruct:free",       # Llama 3.2 3B
    
    # Mistral - Modelos gratuitos confirmados
    "mistralai/mistral-7b-instruct:free",          # Mistral 7B
    
    # Microsoft - Modelos gratuitos
    "microsoft/phi-3-mini-128k-instruct:free",     # Phi-3 Mini
    
    # Qwen - Modelos gratuitos
    "qwen/qwen-2.5-7b-instruct:free",              # Qwen 2.5 7B
    
    # DeepSeek
    "deepseek/deepseek-chat:free",                 # DeepSeek Chat
    
    # Nous Research
    "nousresearch/hermes-3-llama-3.1-405b:free"    # Hermes 3
]

def try_model_with_fallback(messages, api_key):
    """Tenta usar modelos em sequência até encontrar um que funcione"""
    
    for i, model in enumerate(FREE_MODELS):
        try:
            print(f"🔄 Tentando modelo {i+1}/{len(FREE_MODELS)}: {model}")
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Chatbot OpenRouter Français",
                },
                data=json.dumps({
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un assistant francophone intelligent et amical. Tu réponds TOUJOURS en français, peu importe la langue utilisée par l'utilisateur. Tes réponses sont claires, précises et naturelles."
                        }
                    ] + messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }),
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Modèle fonctionne: {model}")
                return response, model
            else:
                print(f"❌ Modèle {model} a échoué (status {response.status_code}): {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout sur le modèle {model}")
        except Exception as e:
            print(f"⚠️ Erreur sur {model}: {str(e)[:100]}")
        
        # Pause entre les tentatives
        if i < len(FREE_MODELS) - 1:
            time.sleep(1)
    
    return None, None

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("=" * 60)
        print("📥 Requête reçue")
        data = request.json
        
        api_key = data.get('api_key') or OPENROUTER_API_KEY
        messages = data.get('messages', [])
        
        print(f"🔑 Clé API présente: {bool(api_key)}")
        print(f"💬 Nombre de messages: {len(messages)}")
        
        if not api_key or api_key == "sk-or-v1-VOTRE-CLE-API-ICI":
            print("❌ Clé API invalide")
            return jsonify({
                'error': 'API key required - Mettez votre clé dans app.py ligne 10'
            }), 400
        
        print("🔄 Test des modèles gratuits...")
        response, model_used = try_model_with_fallback(messages, api_key)
        
        if not response:
            print("❌ Tous les modèles gratuits ont échoué!")
            return jsonify({
                'error': 'Tous les modèles gratuits sont indisponibles. Réessayez plus tard ou utilisez une clé API payante.'
            }), 503
        
        result = response.json()
        print("✅ Réponse reçue avec succès!")
        print(f"📊 Modèle utilisé: {model_used}")
        
        return jsonify({
            'content': result['choices'][0]['message']['content'],
            'model': model_used,
            'usage': result.get('usage', {})
        }), 200
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify({
        'free_models': FREE_MODELS,
        'total': len(FREE_MODELS)
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Serveur opérationnel',
        'free_models_count': len(FREE_MODELS)
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Serveur démarré sur http://localhost:5000")
    print("🇫🇷 Chatbot configuré en français")
    print("🆓 Modèles gratuits vérifiés:", len(FREE_MODELS))
    print("📋 Liste des modèles:")
    for i, model in enumerate(FREE_MODELS, 1):
        print(f"   {i}. {model}")
    print("=" * 60)
    
    if OPENROUTER_API_KEY == "sk-or-v1-VOTRE-CLE-API-ICI":
        print("⚠️  ATTENTION: Modifiez la clé API à la ligne 10!")
    else:
        print("✅ Clé API configurée")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)