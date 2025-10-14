# 🤖 OpenRouter Chatbot with DeepSeek

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-purple.svg)
![DeepSeek](https://img.shields.io/badge/DeepSeek-v3.1-orange.svg)

Elegant web interface to chat with AI models via OpenRouter API. Uses the free DeepSeek Chat v3.1 model with full multilingual support.

## ✨ Features

- 💬 **Modern Chat Interface** - Clean, responsive design
- 🆓 **Free AI Model** - Uses DeepSeek Chat v3.1 (no cost)
- 🌍 **Multilingual** - Supports French and other languages
- 🔒 **Secure API** - Server-side or frontend configuration
- 📝 **Persistent History** - Conversation saved in browser
- ⚡ **Real-time** - Instant responses with loading indicator
- 🎨 **Beautiful UI** - Modern design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key (free): [Get one here](https://openrouter.ai)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Dansoko22md/Free-API-OpenRouter.git
cd chatbot-openrouter
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure your API key**

Edit `backend/app.py` and replace line 10:
```python
OPENROUTER_API_KEY = "sk-or-v1-YOUR-API-KEY-HERE"
```

4. **Launch the server**
```bash
python app.py
```

5. **Open the interface**

Open `frontend/index.html` in your web browser

## 📁 Project Structure

```
chatbot-openrouter/
├── backend/
│   ├── app.py                 # Flask server
│   ├── requirements.txt       # Python dependencies
│   └── venv/                  # Virtual environment (optional)
└── frontend/
    └── index.html             # Web interface (HTML/CSS/JS)
```

## 🔧 Configuration

### Option 1: API Key in Code (Recommended for local use)
Modify `OPENROUTER_API_KEY` in `backend/app.py`:
```python
OPENROUTER_API_KEY = "sk-or-v1-your-actual-key"
```

### Option 2: API Key via Interface
Enter your key directly in the input field on the web page

### Environment Variables (Optional)
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-key"
```

Then modify `app.py`:
```python
import os
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
```

## 💡 Usage

1. Start the Flask backend server:
```bash
cd backend
python app.py
```

2. Open `frontend/index.html` in your browser

3. (Optional) Enter your API key if not configured in code

4. Start chatting! Type your message and press Enter or click Send

## 🌐 API Documentation

### POST `/api/chat`
Send a message to the chatbot

**Request Body:**
```json
{
  "api_key": "sk-or-v1-...",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ]
}
```

**Response:**
```json
{
  "content": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "model": "deepseek/deepseek-chat-v3.1:free",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 20,
    "total_tokens": 35
  }
}
```

### GET `/api/health`
Check server status

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T12:00:00Z"
}
```

## 🛠️ Tech Stack

### Backend
- **Flask** - Lightweight Python web framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Requests** - HTTP library for API calls

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with gradients and animations
- **JavaScript** (Vanilla) - Logic and API interaction

### API
- **OpenRouter** - AI model aggregator
- **DeepSeek Chat v3.1** - Free, high-performance LLM

## 🎨 Customization

### Change AI Model

Edit `backend/app.py`:
```python
"model": "deepseek/deepseek-chat-v3.1:free",  # Change this
```

Available free models on [OpenRouter Models](https://openrouter.ai/models):
- `google/gemma-2-9b-it:free`
- `meta-llama/llama-3-8b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

### Customize Colors

Edit the CSS gradient in `frontend/index.html`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Popular gradients:
- Ocean: `#2E3192 0%, #1BFFFF 100%`
- Sunset: `#FF512F 0%, #DD2476 100%`
- Forest: `#134E5E 0%, #71B280 100%`

### Modify System Prompt

In `app.py`, add a system message:
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    *request_data.get('messages', [])
]
```

## 🐛 Troubleshooting

### Server won't start
- ✅ Check Python version: `python --version` (needs 3.8+)
- ✅ Install dependencies: `pip install -r requirements.txt`
- ✅ Check if port 5000 is available

### API Errors
- ✅ Verify your API key is valid
- ✅ Check OpenRouter credits/limits
- ✅ Ensure internet connection is stable
- ✅ Check [OpenRouter Status](https://status.openrouter.ai)

### CORS Issues
- ✅ Ensure server runs on `localhost:5000`
- ✅ Verify `flask-cors` is installed: `pip show flask-cors`
- ✅ Try a different browser

### Chat not responding
- ✅ Open browser console (F12) to check for errors
- ✅ Verify backend server is running
- ✅ Check network tab for failed requests

## 📊 Performance

- **Response time:** Typically 1-3 seconds
- **Model:** DeepSeek Chat v3.1 (8B parameters)
- **Cost:** $0 (completely free tier)
- **Rate limits:** Check OpenRouter free tier limits

## 🔒 Security Best Practices

⚠️ **Important:** Never commit your API key to version control!

Add to `.gitignore`:
```
backend/venv/
backend/__pycache__/
backend/.env
.env
*.pyc
```

For production:
1. Use environment variables
2. Implement rate limiting
3. Add authentication
4. Use HTTPS
5. Sanitize user inputs

## 📝 License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/amazing-feature`
3. 💾 Commit your changes: `git commit -m 'Add amazing feature'`
4. 📤 Push to the branch: `git push origin feature/amazing-feature`
5. 🔃 Open a Pull Request

### Contribution Ideas
- 🎨 Improve UI/UX design
- 🌐 Add more language support
- 📱 Make it mobile-responsive
- 🔌 Add more AI model options
- 📊 Implement conversation analytics
- 💾 Add database for persistent storage

## 👤 Author

**Your Name**
- GitHub: [@Dansoko22md](https://github.com/Dansoko22md)
- LinkedIn: [linkedin.com](https://www.linkedin.com/in/moussa-dansoko-a6a357172/)

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai) - For providing free AI model access
- [DeepSeek](https://www.deepseek.com) - For the excellent chat model
- [Flask](https://flask.palletsprojects.com/) - For the web framework

## 🔗 Useful Links

- 📚 [OpenRouter Documentation](https://openrouter.ai/docs)
- 🤖 [DeepSeek Models](https://openrouter.ai/models?q=deepseek)
- 🌶️ [Flask Documentation](https://flask.palletsprojects.com/)
- 🎨 [CSS Gradient Generator](https://cssgradient.io/)

## 📈 Roadmap

- [ ] Add conversation export (JSON/PDF)
- [ ] Implement dark/light theme toggle
- [ ] Add voice input support
- [ ] Create Docker containerization
- [ ] Build Chrome extension
- [ ] Add multi-user support
- [ ] Implement conversation search
- [ ] Add code syntax highlighting



---

<div align="center">

⭐ **If this project helps you, please give it a star!** ⭐

Made with ❤️ and lots of ☕

[Report Bug](https://github.com/Dansoko22md/chatbot-openrouter/issues) · [Request Feature](https://github.com/yourusername/chatbot-openrouter/issues)

</div>
