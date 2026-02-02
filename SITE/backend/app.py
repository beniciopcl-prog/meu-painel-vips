from flask import Flask, request, jsonify, render_template, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

COMPROVANTES_FILE = 'comprovantes.json'
DATABASE_FILE = 'database.txt'
ENTREGUES_FILE = 'entregues.txt'

def carregar_pedidos():
    if not os.path.exists(COMPROVANTES_FILE):
        return {}
    try:
        with open(COMPROVANTES_FILE, 'r', encoding='utf-8') as f:
            conteudo = f.read().strip()
            return json.loads(conteudo) if conteudo else {}
    except:
        return {}

def salvar_pedidos(pedidos):
    with open(COMPROVANTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(pedidos, f, indent=4, ensure_ascii=False)

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

@app.route('/solicitar-liberacao', methods=['POST'])
def solicitar():
    data = request.json
    token = data.get("token")
    if not token:
        return jsonify({"error": "Token ausente"}), 400
    
    pedidos = carregar_pedidos()
    pedidos[token] = {
        "status": "pendente",
        "dispositivo": request.user_agent.platform if request.user_agent.platform else "Desconhecido",
        "hora": datetime.now().strftime("%H:%M:%S"),
        "dia": datetime.now().strftime("%d/%m/%Y"),
        "info": data.get("info_pix", "PIX Realizado"),
        "ip": request.remote_addr
    }
    salvar_pedidos(pedidos)
    return jsonify({"success": True})

@app.route('/checar-status')
def checar():
    token = request.args.get("token")
    pedidos = carregar_pedidos()
    status = pedidos.get(token, {}).get("status", "inexistente")
    return jsonify({"status": status})

# --- O PAINEL QUE TINHA SUMIDO ESTÁ DE VOLTA AQUI ---
@app.route('/admin/painel-secreto')
def admin_painel():
    pedidos = carregar_pedidos()
    return render_template('admin_painel.html', pedidos=pedidos)

@app.route('/admin/liberar/<token_cliente>')
def liberar_cliente(token_cliente):
    pedidos = carregar_pedidos()
    if token_cliente in pedidos:
        pedidos[token_cliente]["status"] = "liberado"
        salvar_pedidos(pedidos)
        return f"Sucesso! Token {token_cliente} liberado."
    return "Token nao encontrado.", 404

@app.route('/get-account')
def get_account():
    token = request.args.get("token")
    pedidos = carregar_pedidos()
    
    # Trava: Só libera a conta se o token estiver como "liberado" no seu painel
    if not token or pedidos.get(token, {}).get("status") != "liberado":
        return jsonify({"status": "ERRO", "message": "ACESSO NEGADO: PAGAMENTO NÃO LIBERADO"}), 403

    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            linhas = [l for l in linhas if l.strip()]

            if not linhas:
                return jsonify({"status": "ERRO", "message": "ESTOQUE VAZIO"}), 404
            
            conta_extraida = linhas[0].strip()
            restante = linhas[1:]
            
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                f.writelines(restante)
                
            with open(ENTREGUES_FILE, 'a', encoding='utf-8') as e:
                data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
                e.write(f"{data_hora} | Conta: {conta_extraida} | Token: {token}\n")
                
            return jsonify({"status": "SUCCESS", "full": conta_extraida})
    except:
        return jsonify({"status": "ERRO", "message": "ERRO NO SERVIDOR"}), 500
    return jsonify({"status": "ERRO", "message": "ERRO"}), 404

@app.route('/admin/estoque')
def painel_estoque():
    estoque, vendidas = get_stats()
    return render_template_string('''
        <html>
            <head><title>Estoque</title><script src="https://cdn.tailwindcss.com"></script></head>
            <body class="bg-[#0d0221] text-white flex items-center justify-center min-h-screen text-center p-6">
                <div class="bg-zinc-900 p-10 rounded-3xl border border-purple-500 shadow-2xl">
                    <h1 class="text-2xl font-black mb-6 uppercase">Gestão de Carga</h1>
                    <div class="grid grid-cols-2 gap-6">
                        <div class="bg-purple-900/20 p-6 rounded-xl border border-purple-500/30">
                            <p class="text-xs text-gray-400 font-bold uppercase">No Estoque</p>
                            <p class="text-5xl font-black text-purple-500">{{estoque}}</p>
                        </div>
                        <div class="bg-green-900/20 p-6 rounded-xl border border-green-500/30">
                            <p class="text-xs text-gray-400 font-bold uppercase">Vendidas</p>
                            <p class="text-5xl font-black text-green-500">{{vendidas}}</p>
                        </div>
                    </div>
                    <a href="/admin/painel-secreto" class="mt-8 block bg-purple-600 py-3 rounded-lg font-bold">VOLTAR AO PAINEL DE LIBERAÇÃO</a>
                </div>
            </body>
        </html>
    ''', estoque=estoque, vendidas=vendidas)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
