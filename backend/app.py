from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# ⚠️ METTEZ VOTRE CLÉ API ICI
OPENROUTER_API_KEY = ""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print("📥 Requête reçue")
        data = request.json
        
        # Utiliser la clé API du code OU celle envoyée par le frontend
        api_key = data.get('api_key') or OPENROUTER_API_KEY
        messages = data.get('messages', [])
        
        print(f"🔑 API Key présente: {bool(api_key)}")
        print(f"💬 Nombre de messages: {len(messages)}")
        
        if not api_key or api_key == "sk-or-v1-VOTRE-CLE-API-ICI":
            print("❌ Pas d'API key valide")
            return jsonify({'error': 'API key required - Mettez votre clé dans app.py ligne 10'}), 400
        
        print("📤 Envoi de la requête à OpenRouter (DeepSeek Free)...")
        
        # Ajouter le message système pour forcer le français
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Chatbot OpenRouter Français",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3.1:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un assistant francophone intelligent et amical. Tu réponds TOUJOURS en français, peu importe la langue utilisée par l'utilisateur. Tes réponses sont claires, précises et naturelles."
                    }
                ] + messages
            })
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Erreur API: {response.text}")
            return jsonify({'error': response.text}), response.status_code
        
        result = response.json()
        print("✅ Réponse reçue!")
        
        return jsonify({
            'content': result['choices'][0]['message']['content'],
            'model': result['model'],
            'usage': result.get('usage', {})
        }), 200
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Serveur opérationnel'}), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Serveur démarré sur http://localhost:5000")
    print("🇫🇷 Chatbot configuré en français")
    print("🆓 Modèle gratuit: deepseek/deepseek-chat-v3.1:free")
    if OPENROUTER_API_KEY == "sk-or-v1-VOTRE-CLE-API-ICI":
        print("⚠️  ATTENTION: Modifiez la clé API à la ligne 10 !")
    else:
        print("✅ Clé API configurée")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)