from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

COMPROVANTES_FILE = 'comprovantes.json'

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

@app.route('/solicitar-liberacao', methods=['POST'])
def solicitar():
    data = request.json
    token = data.get("token")
    if not token:
        return jsonify({"error": "Token ausente"}), 400
        
    pedidos = carregar_pedidos()
    
    # Cada token é uma entrada única no banco de dados
    pedidos[token] = {
        "status": "pendente",
        "dispositivo": request.user_agent.platform if request.user_agent.platform else "Desconhecido",
        "hora": datetime.now().strftime("%H:%M:%S"),
        "dia": datetime.now().strftime("%d/%m/%Y"),
        "info": data.get("info_pix", "Sem identificação"),
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
        return f"Cliente {token_cliente} Liberado!"
    return "Token nao encontrado.", 404

@app.route('/get-account')
def get_account():
    return jsonify({"status": "estoque_vazio"}) 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)