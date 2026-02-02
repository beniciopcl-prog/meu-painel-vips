from flask import Flask, request, jsonify, render_template, render_template_string
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

DATABASE_FILE = 'database.txt'
ENTREGUES_FILE = 'entregues.txt'

def get_stats():
    estoque = 0
    vendidas = 0
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            estoque = len([line for line in f if line.strip()])
    if os.path.exists(ENTREGUES_FILE):
        with open(ENTREGUES_FILE, 'r', encoding='utf-8') as f:
            vendidas = len([line for line in f if line.strip()])
    return estoque, vendidas

# Rota de extração SEM VERIFICAÇÃO DE TOKEN
@app.route('/get-account')
def get_account():
    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            # Filtra linhas vazias
            linhas = [l for l in linhas if l.strip()]

            if not linhas:
                return jsonify({"status": "ERRO", "message": "ESTOQUE VAZIO"}), 404
            
            # Pega a primeira conta e remove do estoque
            conta_extraida = linhas[0].strip()
            restante = linhas[1:]
            
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                f.writelines(restante)
                
            # Salva no histórico (opcional, para você saber que saiu)
            with open(ENTREGUES_FILE, 'a', encoding='utf-8') as e:
                data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
                e.write(f"{data_hora} | Conta: {conta_extraida}\n")
                
            return jsonify({"status": "SUCCESS", "full": conta_extraida})
            
    except Exception as e:
        return jsonify({"status": "ERRO", "message": "ERRO NO SERVIDOR"}), 500
        
    return jsonify({"status": "ERRO", "message": "ESTOQUE INDISPONÍVEL"}), 404

# Painel de estoque para você controlar as vendas
@app.route('/admin/estoque')
def painel_estoque():
    estoque, vendidas = get_stats()
    return render_template_string('''
        <html>
            <head>
                <title>Estoque | GamePanel</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-[#0d0221] text-white flex items-center justify-center min-h-screen">
                <div class="bg-zinc-900 p-10 rounded-3xl border border-purple-500 shadow-2xl text-center">
                    <h1 class="text-2xl font-black mb-6 uppercase">Controle de Carga</h1>
                    <div class="flex gap-6">
                        <div class="bg-purple-900/20 p-6 rounded-xl border border-purple-500/30">
                            <p class="text-xs text-gray-400 font-bold uppercase">Disponível</p>
                            <p class="text-5xl font-black text-purple-500">{{estoque}}</p>
                        </div>
                        <div class="bg-green-900/20 p-6 rounded-xl border border-green-500/30">
                            <p class="text-xs text-gray-400 font-bold uppercase">Entregues</p>
                            <p class="text-5xl font-black text-green-500">{{vendidas}}</p>
                        </div>
                    </div>
                    <button onclick="location.reload()" class="mt-8 text-xs text-zinc-500 hover:text-white uppercase font-bold tracking-widest">Atualizar</button>
                </div>
            </body>
        </html>
    ''', estoque=estoque, vendidas=vendidas)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
