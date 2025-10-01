# 🤖 Chatbot OpenRouter avec DeepSeek

Interface web élégante pour discuter avec des modèles d'IA via OpenRouter API. Utilise le modèle gratuit DeepSeek Chat v3.1 avec support complet du français.

## ✨ Caractéristiques

- 💬 Interface de chat moderne et responsive
- 🆓 Utilise le modèle gratuit DeepSeek Chat v3.1
- 🇫🇷 Réponses automatiquement en français
- 🔒 Clé API sécurisée (configuration côté serveur ou frontend)
- 📝 Historique de conversation persistant
- ⚡ Réponses en temps réel avec indicateur de chargement
- 🎨 Design moderne avec animations fluides

## 🚀 Installation

### Prérequis

- Python 3.8+
- Une clé API OpenRouter (gratuite) : [openrouter.ai](https://openrouter.ai)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd chatbot-openrouter
```

2. **Installer les dépendances**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configurer la clé API**

Ouvrez `backend/app.py` et modifiez la ligne 10 :
```python
OPENROUTER_API_KEY = "sk-or-v1-VOTRE-CLE-API-ICI"
```

4. **Lancer le serveur**
```bash
python app.py
```

5. **Ouvrir l'interface**

Ouvrez `frontend/index.html` dans votre navigateur

## 📁 Structure du projet

```
chatbot-openrouter/
├── backend/
│   ├── app.py                 # Serveur Flask
│   ├── requirements.txt       # Dépendances Python
│   └── venv/                  # Environnement virtuel
└── frontend/
    └── index.html             # Interface web
```

## 🔧 Configuration

### Option 1 : Clé API dans le code (recommandé)
Modifiez `OPENROUTER_API_KEY` dans `app.py`

### Option 2 : Clé API dans l'interface
Entrez votre clé directement dans le champ prévu sur la page web

## 💡 Utilisation

1. Lancez le serveur backend
2. Ouvrez `index.html` dans votre navigateur
3. Entrez votre clé API (si non configurée dans le code)
4. Commencez à discuter !

## 🌐 API Endpoints

### POST `/api/chat`
Envoie un message au chatbot

**Body:**
```json
{
  "api_key": "sk-or-v1-...",
  "messages": [
    {"role": "user", "content": "Bonjour"}
  ]
}
```

**Response:**
```json
{
  "content": "Bonjour ! Comment puis-je vous aider ?",
  "model": "deepseek/deepseek-chat-v3.1:free",
  "usage": {...}
}
```

### GET `/api/health`
Vérifie l'état du serveur

## 🛠️ Technologies utilisées

- **Backend:** Flask, Flask-CORS, Requests
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **API:** OpenRouter (DeepSeek Chat v3.1)

## 🎨 Personnalisation

### Changer le modèle

Dans `app.py`, modifiez la ligne du modèle :
```python
"model": "deepseek/deepseek-chat-v3.1:free",
```

Modèles gratuits disponibles sur [OpenRouter](https://openrouter.ai/models)

### Modifier les couleurs

Dans `index.html`, ajustez le gradient CSS :
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 🐛 Dépannage

### Le serveur ne démarre pas
- Vérifiez que Python 3.8+ est installé
- Assurez-vous que toutes les dépendances sont installées

### Erreur d'API
- Vérifiez que votre clé API est valide
- Assurez-vous d'avoir des crédits OpenRouter
- Vérifiez votre connexion internet

### CORS Errors
- Assurez-vous que le serveur tourne sur `localhost:5000`
- Vérifiez que `flask-cors` est installé

## 📝 Licence

MIT License - Libre d'utilisation et de modification

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ouvrir des issues pour signaler des bugs
- Proposer des pull requests pour des améliorations
- Suggérer de nouvelles fonctionnalités

## 👤 Auteur

Créé avec ❤️ pour faciliter l'accès aux modèles d'IA

## 🔗 Liens utiles

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [DeepSeek Models](https://openrouter.ai/models?q=deepseek)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

⭐ Si ce projet vous est utile, n'oubliez pas de mettre une étoile !