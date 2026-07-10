from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ============================================================
# SUA CHAVE API DO GROQ
# ============================================================
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# SEUS MODELOS (exatamente como você usa)
# ============================================================
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",      # Melhor qualidade
    "llama-3.1-70b-versatile",      # Alta qualidade
    "llama-3.1-8b-instant",         # Rápido e bom
    "gemma2-9b-it",                 # Google Gemma 2
    "deepseek-r1-distill-llama-70b" # DeepSeek
]

# ============================================================
# SISTEMA DE MEMÓRIA
# ============================================================

# Arquivo onde as conversas serão salvas
MEMORY_FILE = "conversas.json"

# Carregar conversas salvas
def load_conversations():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Salvar conversas
def save_conversations(conversations):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

# Inicializar memória
conversations = load_conversations()

# ============================================================
# PERSONALIDADES
# ============================================================
PERSONALITIES = {
    "default": "Você é um assistente útil, amigável e inteligente. Responda SEMPRE em português, de forma clara e natural.",
    
    "professor": """Você é um professor experiente e paciente.
Você ensina qualquer assunto de forma simples, didática e com exemplos práticos.
Você adora explicar conceitos complexos de maneira fácil de entender.
Você sempre pergunta se o aluno entendeu e incentiva perguntas.
SEMPRE responda em português.""",

    "programador": """Você é um programador sênior especialista em Python, JavaScript e desenvolvimento web.
Você escreve código limpo, bem comentado e explicado linha por linha.
Você sugere as melhores práticas e otimizações.
Você ajuda a debugar erros e ensina lógica de programação.
SEMPRE responda em português.""",

    "chef": """Você é um chef de cozinha renomado.
Você dá receitas deliciosas com ingredientes acessíveis.
Você explica técnicas culinárias e substituições inteligentes.
Você ama compartilhar dicas de cozinha e harmonização.
SEMPRE responda em português.""",

    "financeiro": """Você é um consultor financeiro especialista em finanças pessoais.
Você ajuda a organizar orçamentos, economizar dinheiro e investir.
Você dá conselhos práticos e realistas para cada perfil.
Você ensina sobre juros, ações, fundos e planejamento.
SEMPRE responda em português.""",

    "fitness": """Você é um personal trainer e nutricionista.
Você dá dicas de exercícios, alimentação saudável e bem-estar.
Você motiva as pessoas a terem hábitos mais saudáveis.
Você adapta os conselhos para cada nível de condicionamento.
SEMPRE responda em português.""",

    "coach": """Você é um coach de desenvolvimento pessoal e carreira.
Você ajuda as pessoas a definirem metas, superarem desafios e crescerem.
Você faz perguntas poderosas que geram reflexão.
Você dá conselhos motivacionais e práticos para a vida.
SEMPRE responda em português."""
}

# ============================================================
# FUNÇÃO PARA CRIAR PROMPT COM HISTÓRICO
# ============================================================
def build_prompt_with_memory(session_id, personality_key, user_message, max_history=10):
    """Constrói o prompt incluindo o histórico da conversa"""
    
    # Pega a personalidade
    system_prompt = PERSONALITIES.get(personality_key, PERSONALITIES["default"])
    
    # Recupera o histórico da sessão
    history = conversations.get(session_id, [])
    
    # Pega as últimas mensagens (limitado por max_history)
    recent_history = history[-max_history:] if history else []
    
    # Constrói o prompt com histórico
    prompt = system_prompt + "\n\n"
    prompt += "Histórico da conversa:\n"
    prompt += "-" * 40 + "\n"
    
    for msg in recent_history:
        role = "Usuário" if msg['role'] == 'user' else "Assistente"
        prompt += f"{role}: {msg['content']}\n"
    
    prompt += "-" * 40 + "\n"
    prompt += f"Usuário: {user_message}\n"
    prompt += "Assistente:"
    
    return prompt

# ============================================================
# ROTA PRINCIPAL
# ============================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        personality_key = data.get('personality', 'default')
        session_id = data.get('session_id', 'default')
        
        if not messages:
            return jsonify({'error': 'Nenhuma mensagem'}), 400

        user_message = messages[-1]['content'] if messages else ""

        print("=" * 60)
        print(f"💬 Pergunta: {user_message[:100]}...")
        print(f"🎭 Personalidade: {personality_key}")
        print(f"🆔 Sessão: {session_id}")

        # ===== SALVAR MENSAGEM DO USUÁRIO =====
        if session_id not in conversations:
            conversations[session_id] = []
        
        conversations[session_id].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        save_conversations(conversations)

        # ===== CRIAR PROMPT COM HISTÓRICO =====
        prompt = build_prompt_with_memory(session_id, personality_key, user_message)

        # ===== TENTAR CADA MODELO =====
        for model in AVAILABLE_MODELS:
            try:
                print(f"🔄 Tentando: {model}")

                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                response_text = completion.choices[0].message.content
                print(f"✅ Sucesso com: {model}")

                # ===== SALVAR RESPOSTA DO BOT =====
                conversations[session_id].append({
                    'role': 'assistant',
                    'content': response_text,
                    'timestamp': datetime.now().isoformat()
                })
                save_conversations(conversations)

                # ===== CONTAR TOTAL DE MENSAGENS =====
                total_messages = len(conversations[session_id])

                return jsonify({
                    'content': response_text,
                    'model': f'groq/{model}',
                    'personality': personality_key,
                    'session_id': session_id,
                    'history_count': total_messages
                }), 200

            except Exception as e:
                print(f"❌ {model} falhou: {str(e)[:100]}")
                continue

        return jsonify({'error': 'Nenhum modelo disponível'}), 503

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# ROTA PARA LIMPAR MEMÓRIA DE UMA SESSÃO
# ============================================================
@app.route('/api/clear_memory/<session_id>', methods=['DELETE'])
def clear_memory(session_id):
    if session_id in conversations:
        conversations[session_id] = []
        save_conversations(conversations)
        return jsonify({'message': f'Memória da sessão {session_id} limpa'}), 200
    return jsonify({'error': 'Sessão não encontrada'}), 404

# ============================================================
# ROTA PARA VER HISTÓRICO DE UMA SESSÃO
# ============================================================
@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    if session_id in conversations:
        return jsonify({
            'session_id': session_id,
            'history': conversations[session_id],
            'count': len(conversations[session_id])
        }), 200
    return jsonify({'history': [], 'count': 0}), 200

# ============================================================
# ROTA DE HEALTH CHECK
# ============================================================
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Servidor Groq com Memória',
        'personalities': list(PERSONALITIES.keys()),
        'models': AVAILABLE_MODELS,
        'sessions': len(conversations),
        'memory_file': MEMORY_FILE
    }), 200

# ============================================================
# INICIALIZAÇÃO
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🧠 CHATBOT GROQ COM MEMÓRIA")
    print("🚀 Rodando em http://localhost:5000")
    print(f"📁 Arquivo de memória: {MEMORY_FILE}")
    print(f"💾 Sessões salvas: {len(conversations)}")
    print("🎭 Personalidades disponíveis:")
    for p in PERSONALITIES.keys():
        print(f"   - {p}")
    print("=" * 60)

    if GROQ_API_KEY == "SUA_CHAVE_GROQ_AQUI":
        print("⚠️  ATENÇÃO: Coloque sua chave API Groq!")
        print("📌 Obtenha em: https://console.groq.com/keys")
    else:
        print("✅ Chave API configurada")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)