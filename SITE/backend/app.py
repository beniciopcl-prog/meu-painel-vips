from flask import Flask, jsonify
from flask_cors import CORS
import random
import os

app = Flask(__name__)
# O CORS é essencial para que o seu site (Frontend) consiga acessar o Python (Backend)
CORS(app)

# Caminhos dos arquivos - Usando caminhos absolutos para evitar erros na nuvem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.txt')
LOG_PATH = os.path.join(BASE_DIR, 'entregues.txt')

# --- ROTA DO GERADOR (O que o cliente usa) ---
@app.route('/get-account', methods=['GET'])
def get_account():
    if not os.path.exists(DB_PATH):
        return jsonify({"status": "ERROR", "message": "Database nao encontrado"}), 500

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        linhas = [l.strip() for l in f.readlines() if l.strip()]

    if not linhas:
        return jsonify({"status": "EXHAUSTED", "message": "Estoque vazio!"}), 404

    conta_sorteada = random.choice(linhas)
    # Filtra para remover a conta sorteada do banco
    novas_linhas = [l for l in linhas if l != conta_sorteada]

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        for linha in novas_linhas:
            f.write(linha + '\n')

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{conta_sorteada}\n")

    # Divide usuario e senha
    try:
        user, senha = conta_sorteada.split(':', 1)
    except:
        user, senha = conta_sorteada, "S/S"

    return jsonify({
        "status": "SUCCESS",
        "username": user,
        "password": senha,
        "full": conta_sorteada
    })

# --- ROTA DE ADMIN (O seu controle secreto) ---
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    estoque = 0
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            estoque = len([l for l in f.readlines() if l.strip()])
    
    vendas = 0
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            vendas = len([l for l in f.readlines() if l.strip()])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - GamePanel</title>
        <style>
            body {{ background: #0a0514; color: #a855f7; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ border: 1px solid #a855f7; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 0 20px rgba(168,85,247,0.2); }}
            .stat {{ font-size: 3em; color: white; }}
            .label {{ color: #666; text-transform: uppercase; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>MONITORAMENTO</h1>
            <div class="label">Estoque</div><div class="stat">{estoque}</div>
            <br>
            <div class="label">Entregues</div><div class="stat" style="color:#22c55e">{vendas}</div>
        </div>
    </body>
    </html>
    """

# --- ROTA DE STATUS ---
@app.route('/status', methods=['GET'])
def check_status():
    return jsonify({"status": "ONLINE", "server": "GamePanel Pro"}), 200

# --- CONFIGURAÇÃO DE PORTA PARA DEPLOY ---
if __name__ == '__main__':
    # O Render/Railway definem a porta automaticamente pela variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Servidor GamePanel Pro em execucao na porta {port}!")
    app.run(host='0.0.0.0', port=port)