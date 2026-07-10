from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# COLOQUE SUA CHAVE API DO GOOGLE AQUI
GOOGLE_API_KEY = "AQ.Ab8RN6I-GgYuh9kQ1Fj-ORob_rpBksMagRIwJ4VN9IdZ6rN8Rg"

# Configurar o Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Modelos Gemini gratuitos disponíveis (atualizados em 2026)
AVAILABLE_MODELS = [
    'gemini-2.0-flash',           # Gemini 2.0 Flash (recomendado)
    'gemini-2.0-flash-lite',      # Gemini 2.0 Flash Lite (mais rápido)
    'gemini-1.5-flash',           # Gemini 1.5 Flash
    'gemini-1.5-pro',             # Gemini 1.5 Pro
    'gemini-pro',                 # Gemini Pro (legado)
    'gemini-1.0-pro'              # Gemini 1.0 Pro (legado)
]

# Usar o primeiro modelo disponível
def get_model():
    for model_name in AVAILABLE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            # Testar se o modelo funciona
            test_response = model.generate_content("test")
            print(f"✅ Modelo disponível: {model_name}")
            return model, model_name
        except Exception as e:
            print(f"⚠️ Modelo {model_name} indisponível: {str(e)[:50]}")
            continue
    return None, None

model, model_name = get_model()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("=" * 60)
        print("📥 Requête reçue")
        data = request.json
        messages = data.get('messages', [])
        
        print(f"💬 Nombre de messages: {len(messages)}")
        
        if not messages:
            return jsonify({'error': 'Aucun message'}), 400
        
        user_message = messages[-1]['content'] if messages else ""
        
        prompt = f"""
        Tu es un assistant francophone intelligent et amical.
        Tu réponds TOUJOURS en français, peu importe la langue utilisée.
        Tes réponses sont claires, précises et naturelles.
        
        Message de l'utilisateur: {user_message}
        
        Réponse en français:
        """
        
        print(f"📤 Envoi au Gemini ({model_name}): {user_message[:50]}...")
        
        response = model.generate_content(prompt)
        
        print("✅ Réponse reçue!")
        
        return jsonify({
            'content': response.text,
            'model': f'google/{model_name}',
            'usage': {'prompt_tokens': 0, 'completion_tokens': 0}
        }), 200
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """Listar todos os modelos disponíveis"""
    try:
        available = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available.append(m.name)
        return jsonify({'models': available}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Serveur Gemini opérationnel',
        'model': model_name if model else 'Nenhum modelo disponível'
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Serveur Gemini démarré sur http://localhost:5000")
    print("🇫🇷 Chatbot configuré en français")
    print(f"🤖 Modèle: {model_name if model else 'Nenhum encontrado'}")
    print("📝 60 requêtes/minutes gratuites")
    print("=" * 60)
    
    if model:
        print("✅ Modèle configuré avec succès!")
    else:
        print("❌ Aucun modèle disponible. Vérifiez votre clé API.")
        print("📌 Obtenez une clé sur: https://aistudio.google.com/apikey")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
