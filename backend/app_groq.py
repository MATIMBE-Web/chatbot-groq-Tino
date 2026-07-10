from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# SUA CHAVE API DO GROQ (pegue em https://console.groq.com/keys)
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# Modelos disponíveis na Groq (atualizados 2026)
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",      # Melhor qualidade
    "llama-3.1-70b-versatile",      # Alta qualidade
    "llama-3.1-8b-instant",         # Rápido e bom
    "gemma2-9b-it",                 # Google Gemma 2
    "deepseek-r1-distill-llama-70b" # DeepSeek
]

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        user_message = messages[-1]['content'] if messages else ""
        
        print("=" * 60)
        print(f"📥 Mensagem: {user_message[:50]}...")
        
        # Tentar cada modelo até um funcionar
        for model in AVAILABLE_MODELS:
            try:
                print(f"🔄 Tentando: {model}")
                
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Tu es un assistant français. Réponds TOUJOURS en français, de manière claire et naturelle."},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                response_text = completion.choices[0].message.content
                print(f"✅ Sucesso com: {model}")
                
                return jsonify({
                    'content': response_text,
                    'model': f'groq/{model}'
                }), 200
                
            except Exception as e:
                print(f"❌ {model} falhou: {str(e)[:100]}")
                continue
        
        return jsonify({'error': 'Nenhum modelo disponível'}), 503
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """Listar modelos disponíveis"""
    return jsonify({
        'models': AVAILABLE_MODELS,
        'default': AVAILABLE_MODELS[0]
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Serveur Groq opérationnel',
        'models': AVAILABLE_MODELS
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Serveur Groq démarré sur http://localhost:5000")
    print("🇫🇷 Chatbot configuré en français")
    print("📋 Modèles disponibles:")
    for i, model in enumerate(AVAILABLE_MODELS, 1):
        print(f"   {i}. {model}")
    print("=" * 60)
    print("🔑 Utilisez votre clé API Groq")
    print("📌 Obtenez une clé: https://console.groq.com/keys")
    print("=" * 60)
    
    if GROQ_API_KEY == "SUA_CHAVE_GROQ_AQUI":
        print("⚠️  ATTENTION: Modifiez la clé API Groq!")
    else:
        print("✅ Clé API configurée")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
